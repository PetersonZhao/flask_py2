# -*- coding: utf-8 -*-
from flask import current_app, jsonify, json

from ihome import redis_store, constants
from ihome.api_1_0 import api
from ihome.models import Area
from ihome.utils.response_code import RET


@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    # 先尝试从redis中获取数据
    try:
        area_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
        area_json = None

    if area_json is None:
        # 查询数据库,获取城区信息
        try:
            area_list = Area.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询城区信息错误")

        # 遍历列表, 处理每一个对象, 转换一下对象的属性名
        areas = []
        for area in area_list:
            areas.append(area.to_dict())

        # 将数据转换为json
        area_json = json.dumps(areas)
        # 将数据在redis中保存一份缓存
        try:
            redis_store.setex("area_info", constants.AREA_INFO_REDIS_EXPIRES, area_json)
        except Exception as e:
            current_app.logger.error(e)
    else:
        # 表示redis中有缓存, 直接使用缓存数据
        current_app.logger.info("hit redis cache area info")

    # return jsonify(errno=RET.OK, errmsg="查询城区信息成功", data={"areas": areas})
    return '{"errno": 0, "errmsg": "查询城区信息成功", "data": {"areas": %s}}' % area_json, 200, \
           {"Content-Type": "application/json"}
