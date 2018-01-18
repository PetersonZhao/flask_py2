# -*- coding: utf-8 -*-
from . import api
from ihome import db, models
from flask import current_app


@api.route("/")
def index():
    return "index page"
