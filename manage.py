# -*- coding: utf-8 -*-
# import redis
# from flask import Flask
# from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import CSRFProtect
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from ihome import create_app, db

app = create_app("develop")
# db = SQLAlchemy(app)

# 创建管理工具对象
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)

# redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 为flask补充csrf防护机制
# csrf = CSRFProtect(app)
# 将flask里的session数据保存到redis中
# Session(app)
# @app.route("/")
# def index():
#     return "index page"


if __name__ == '__main__':
    app.run()
