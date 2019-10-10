# coding:utf-8

from . import api
from ihome import db, models
# import logging
from flask import current_app


@api.route("/index")
def index():
    #print("hello")
    # logging.error()   # 记录错误信息
    # logging.warn()   # 警告
    # logging.info()   # 信息
    # logging.debug()   # 调试
    current_app.logger.error("error info")
    current_app.logger.warn("warn info")
    current_app.logger.info("info info")
    current_app.logger.debug("debug info")
    return "index page"


# @api.route("/house/<int:house_id>", methods=["GET"])
# def get_house_detail(house_id):
#     """获取当前房屋的详细信息"""
#     # 获取用户的id
#     user_id = session.get("user_id", "-1")
#     # 从缓存中获取房屋的信息
#     try:
#         json_dict = redis_store.get("house_detail_message_%s" % house_id)
#     except Exception as e:
#         json_dict = None
#         current_app.logger.error(e)
#
#     # 判断是否取出成功
#     if json_dict:
#         current_app.logger.info(" hite the house detail redis")
#         return json_dict, 200, {"Content-Type": "application/json"}
#
#     # 获取当前房屋对象
#     try:
#         house = House.query.get(house_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR, errmsg="获取当前数据库信息失败")
#
#     # 判断房屋是否存在
#     if not house:
#         return jsonify(errno=RET.NODATA, errmsg="当前房屋不存在")
#
#     # 将房屋信息转换为json字典
#     house_dict = house.to_full_dict()
#     data_dict = {"user_id": user_id, "house_dict": house_dict}
#     resp_dict = dict(errno=RET.OK, errmsg="获取成功", data=data_dict)
#     json_dict = json.dumps(resp_dict)
#
#     #  将房屋信息保存到redis缓存中
#     try:
#         redis_store.setex("house_detail_message_%s" % house_id, constants.HOUSE_DETAIL_SAVE_TIME, json_dict)
#     except Exception as e:
#         current_app.logger.error(e)
#
#     return json_dict, 200, {"Content-Type": "application/json"}


# logging.basicConfig(level=logging.ERROR)



