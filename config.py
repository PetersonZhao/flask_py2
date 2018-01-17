# -*- coding: utf-8 -*-
import redis


class Config(object):
    """工程的配置信息"""
    SECRET_KEY = "aksdfhjasdf[]4354o()*&"
    # DEBUG = True

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


class DevelopmentConfig(Config):
    """开发模式使用的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产模式 线上模式的配置信息"""
    pass


config_dict = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
