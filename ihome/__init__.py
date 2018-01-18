# -*- coding: utf-8 -*-
import redis
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
# import api_1_0
from config import config_dict
from flask import Flask

# 为了方便其他模块调用db，将其放在create外面，延迟初始化
db = SQLAlchemy()
# 构建redis链接对象
redis_store = None

# 为flask补充csrf防护机制
csrf = CSRFProtect()


def create_app(config_name):
    app = Flask(__name__)

    conf = config_dict[config_name]

    app.config.from_object(conf)

    # 延迟初始化数据库
    db.init_app(app)
    csrf.init_app(app)

    # 将flask里的session数据保存到redis中
    Session(app)

    global redis_store
    redis_store = redis.StrictRedis(host=conf.REDIS_HOST, port=conf.REDIS_PORT)

    # 注册蓝图
    import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1_0")
    return app
