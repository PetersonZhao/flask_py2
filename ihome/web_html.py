# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf
# from . import RegexConverter

html = Blueprint("html", __name__)
# 提供静态的html文件

@html.route("/<re(r'.*'):file_name>")
def get_html_file(file_name):
    """提供html文件"""
    # 根据用户访问的路径指明的html文件夹，提供相对应的html文件
    if not file_name:
        # 表示用户访问的是/
        file_name = "index.html"

    if file_name != "favicon.ico":
        file_name = "html/" + file_name
    # 使用WTF帮助我们生成csrf字符串
    csrf_token = generate_csrf()
    # 生成csrf_token，让用户在首次访问网站的时候就获得csrf
    resp = make_response(current_app.send_static_file(file_name))
    resp.set_cookie("csrf_token", csrf_token)
    return resp
    # pass
