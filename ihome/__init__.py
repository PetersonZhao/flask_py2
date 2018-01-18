# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler

import redis
import logging
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

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)


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
