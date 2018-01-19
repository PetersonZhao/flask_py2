# -*- coding: utf-8 -*-
from flask import current_app, jsonify, make_response

from ihome.utils.response_code import RET
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants


@api.route("/image_code/<image_code_id>")
def get_image_code(image_code_di):
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
        redis_store.setex("image_code_%s" % image_code_di, constants.IMAGE_CODE_REDIS_EXPIRES, text)
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
