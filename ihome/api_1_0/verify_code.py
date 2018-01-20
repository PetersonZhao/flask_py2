# -*- coding: utf-8 -*-
import random

from flask import current_app, jsonify, make_response, request

from ihome.libs.yuntongxun.sms import CCP
from ihome.models import User
from ihome.utils.response_code import RET
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants


@api.route("/image_code/<image_code_id>")
def get_image_code(image_code_id):
    """提供图片验证码"""
    # 获取参数
    # 校验参数
    # 业务处理
    # 生成验证码图片
    # 名字，真实值，图片二进制
    name, text, image_data = captcha.generate_captcha()
    # 保存验证码的真实值与编号
    # 考虑到验证码保存不需要长期留存，还要维护验证码的有效期，故使用redis保存
    # 数据结构应该是哈希或者字符串
    # 因为每个验证码的有效期都不同，所以使用字符串
    # redis_store.set("image_code_%s" % image_code_di, text)
    # redis_store.expires("image_code_%s" % image_code_di, constants.IMAGE_CODE_REDIS_EXPIRES)
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno": RET.DBERR,
            # 在实际开发中，一定要使用英文
            "errmsg": "保存验证码失败"
        }
        return jsonify(resp)
    # 返回验证码图片,需带上响应头，否则浏览器不识别
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp
    # pass


@api.route("/sms_codes/<re(r'1[345678]\d{9}'):mobile>")
def send_sms_code(mobile):
    """发送短信验证码"""
    # 获取参数
    image_code_id = request.args.get("image_code_id")
    image_code = request.args.get("image_code")
    # 校验参数
    if not all([image_code_id, image_code]):
        resp = {
            "errno": RET.PARAMERR,
            "errmsg": "参数不完整"
        }
        return jsonify(resp)
    # 取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno": RET.DBERR,
            "errmsg": "获取图片验证码失败"
        }
        return jsonify(resp)

    # 判断验证码的有效期
    if real_image_code is None:
        # 表示redis中没有这个数据
        resp = {
            "errno": RET.NODATA,
            "errmsg": "图片验证码过期"
        }
        return jsonify(resp)

    # 验证完毕后，直接删除验证码，防止用户暴力测试同一个验证码
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写的验证码与真实的验证码
    if real_image_code.lower() != image_code.lower():
        # lower可以将所有字母变成小写
        # 表示用户填写有误
        resp = {
            "errno": RET.DATAERR,
            "errmsg": "图片验证码有误"
        }
        return jsonify(resp)

    # 判断用户手机号是否注册过
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        # resp = {
        #     "errno": RET.DBERR,
        #     "errmsg": ""
        # }
        # return jsonify(resp)
    else:
        if user is not None:
            # 用户已经注册过
            resp = {
                "errno": RET.DATAEXIST,
                "errmsg": "用户手机号已经注册过"
            }
            return jsonify(resp)

    # 创建短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno": RET.DBERR,
            "errmsg": "保存短信验证码异常"
        }
        return jsonify(resp)

    # 发送短信验证码
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno": RET.THIRDERR,
            "errmsg": "发送短信验证码异常"
        }
        return jsonify(resp)
    # 返回值
    if result == 0:
        # 发送成功
        resp = {
            "errno": RET.OK,
            "errmsg": "发送短信验证码成功"
        }
        return jsonify(resp)
    else:
        resp = {
            "errno": RET.THIRDERR,
            "errmsg": "发送短信验证码失败"
        }
        return jsonify(resp)
