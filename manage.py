# -*- coding: utf-8 -*-
import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

app = Flask(__name__)


class Config(object):
    """工程的配置信息"""
    DEBUG = True

    # 数据库MySQL的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 配置redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session用到的配置信息
    # 指明保存到redis中
    SESSION_TYPE = "redis"
    # 让cookie中的session_id被加密签名处理
    SESSION_USE_SIGNER = True
    # 使用的redis实例
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # session有效期，单位秒
    PERMANENT_SESSION_LIFETIME = 86400


app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 为flask补充csrf防护机制
csrf = CSRFProtect(app)

# 将flask里的session数据保存到redis中
Session(app)


@app.route("/")
def index():
    return "index page"


if __name__ == '__main__':
    app.run()
