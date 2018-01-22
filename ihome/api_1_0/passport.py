# -*- coding: utf-8 -*-
import re
from flask import request, jsonify, current_app, session

from ihome import redis_store, db, constants
from ihome.models import User
from ihome.utils.common import login_required
from ihome.utils.response_code import RET
from . import api


# POST /api/v1_0/user
@api.route("/user", methods=["POST"])
def register():
    """用户注册"""
    # 接收参数， 手机号， 短信验证码， 密码
    # 此方法能把json数据转化为字典
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    # 校验参数
    if not all([mobile, sms_code, password]):
        resp = {
            "errno": RET.PARAMERR,
            "errmsg": "参数不完整"
        }
        return jsonify(resp)

    # 判断手机格式
    if not re.match(r"1[345678]\d{9}", mobile):
        resp = {
            "erron": RET.DATAERR,
            "errmsg": "手机号格式错误"
        }
        return jsonify(resp)
    # 业务逻辑
    # 获取真实的短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "erron": RET.DBERR,
            "errmsg": "查询验证码错误"
        }
        return jsonify(resp)

    # 判断短信验证码是否过期
    if real_sms_code is None:
        resp = {
            "errno": RET.NODATA,
            "errmsg": "短信验证码过期"
        }
        return jsonify(resp)
    # 对于用户输入的短信验证码是否正确
    if real_sms_code != sms_code:
        resp = {
            "errno": RET.DATAERR,
            "errmsg": "短信验证码错误"
        }
        return jsonify(resp)

    # 删除短信验证码
    # 当验证码验证通过之后删除
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 删除短信验证码
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断手机号是否注册
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     resp = {
    #         "errno": RET.DBERR,
    #         "errmsg": "数据库异常"
    #     }
    #     return jsonify(resp)
    #
    # if user is not None:
    #     # 表示已经注册过
    #     resp = {
    #         "errno": RET.DATAEXIST,
    #         "errmsg": "用户手机号已经注册"
    #     }
    #     return jsonify(resp)

    # 保存用户的数据到数据库中

    user = User(name=mobile, mobile=mobile)
    # 对于password属性的设置，会调用属性方法，进行加密操作
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 当出现异常时,回滚
        db.session.rollback()
        # 表示已经注册过
        resp = {
            "errno": RET.DATAEXIST,
            "errmsg": "用户手机号已经注册"
        }
        return jsonify(resp)

    # 利用session记录用户的登录状态
    session["user_id"] = user.id
    session["user_name"] = mobile
    session["mobile"] = mobile
    # 返回值
    resp = {
        "errno": RET.OK,
        "errmsg": "注册成功"
    }
    return jsonify(resp)


@api.route("/passport", methods=["POST"])
def login():
    """用户登陆"""
    # 获取json数据
    req_dict = request.get_json()
    user_mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    if not all([user_mobile, password]):
        resp = {
            "errno": RET.PARAMERR,
            "errmsg": "参数不完整"
        }
        return jsonify(resp)

    # 判断手机号格式
    if not re.match(r"1[345678]\d{9}", user_mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 判断用户的错误次数
    # 从redis中获取错误次数
    # 获取登陆用户的ip
    user_ip = request.remote_addr
    try:
        # 获取用户ip的登陆次数
        access_counts = redis_store.get("access_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 如果有错误次数记录, 并且超过最大次数, 直接返回
        if access_counts is not None and access_counts >= constants.LOGIN_ERROR_MAX_NUM:
            return jsonify(errno=RET.REQERR, errmsg="用户登陆过于频繁")

    # 查询数据库,判断用户名与密码
    try:
        user = User.query.filter_by(mobile=user_mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno": RET.DBERR,
            "errmsg": "查询数据库错误"
        }
        return jsonify(resp)

    if user is None or not user.check_password(password):
        # 用户不存在或密码错误
        # 出现错误,累加错误次数
        # access_counts += 1
        try:
            # 将key中储存的数字值+1,如果不存在,则初始化为0
            redis_store.incr("access_%s" % user_ip)
            # 设置有效期
            redis_store.expire("access_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)

        except Exception as e:
            current_app.logger.error(e)
        resp = {
            "errno": RET.LOGINERR,
            "errmsg": "用户名或密码错误"
        }
        return jsonify(resp)
    # 校验密码
    # try:
    #     result = user.check_password(password)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     resp = {
    #         "errno": RET.DBERR,
    #         "errmsg": "查询数据库错误"
    #     }
    #     return jsonify(resp)
    #
    # if result is True:
    # 密码正确

    # 登陆成功,删除用户的错误计数
    try:
        redis_store.delete("access_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)

    # 利用session记录用户的登陆状态
    session["user_id"] = user.id
    session["user_name"] = user_mobile
    session["user_id"] = user_mobile
    resp = {
        "errno": RET.OK,
        "errmsg": "登陆成功"
    }
    return jsonify(resp)
    # pass
    # else:
    #     # 密码错误
    #     resp = {
    #         "errno": RET.PWDERR,
    #         "errmsg": "密码错误"
    #     }
    #     return jsonify(resp)
    #     # pass
    # user = User()
    # user.check_password()
    # pass


@api.route("/session", methods=["POST"])
def check_login():
    """检查用户的登陆状态"""
    # 从seesion中取user_id
    # req_dict = request.get_json()
    # user_session = req_dict.get("session")
    try:
        user_name = session.get("user_name")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user_name is not None:
            # 用户已登陆
            resp = {
                "user_name": user_name,
                "errno": RET.OK,
                "errmsg": "用户已登陆"
            }
            return jsonify(resp)
        else:
            # 用户未登录
            resp = {
                "errno": RET.SESSIONERR,
                "errmsg": "用户未登陆"
            }
            return jsonify(resp)


@api.route("/session", methods=["DELETE"])
@login_required
def logout():
    """用户登出"""
    # 清除session数据
    try:
        session.clear()
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            "errno": RET.SERVERERR,
            "errmsg": "用户登出失败"
        }
        return jsonify(resp)
    else:
        resp = {
            "errno": RET.OK,
            "errmsg": "用户已登出"
        }
        return jsonify(resp)

    # session.clear()
    # 返回给前端操作是否成功
