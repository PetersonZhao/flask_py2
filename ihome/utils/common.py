# -*- coding: utf-8 -*-
from functools import wraps

from flask import session, g, jsonify
from werkzeug.routing import BaseConverter

from ihome.utils.response_code import RET


class RegexConverter(BaseConverter):
    """自定义的接收正则表达式的路由转换器"""
    def __init__(self, url_map, regex):
        """regex是在路由中填写的正则表达式"""
        super(RegexConverter, self).__init__(url_map)
        self.regex = regex


def login_required(func):
    """检查用户是否登陆"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None:
            # 表示用户已经登陆
            # 使用g对象保存userid
            g.user_id = user_id
            return func(*args, **kwargs)
        else:
            # 用户未登陆
            resp = {
                "errno": RET.SESSIONERR,
                "errmsg": "用户未登录"
            }
            return jsonify(resp)
    return wrapper
