# coding: utf-8

from . import api
from ihome.utils.commons import login_check
from flask import g, current_app, jsonify, request, session
from ihome import db
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome import constants
from ihome.models import User


@api.route("/users/avatar", methods=["POST"])
@login_check
def save_image_avatar():
    """
    保存头像图片
    参数  图片（多媒体文件）  id
    :return:
    """
    # 获取图片文件
    image_file = request.files.get("avatar")
    user_id = g.get("user_id")

    # 数据校验
    if image_file is None:
        return jsonify(errno=RET.NODATA, errmsg="图片未上传")

    image_data = image_file.read()

    # 上传图片到青牛
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片到青牛失败")

    # 将上传图片后的链接地址保存到数据库
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": image_name})
        db.session.commit()
    except Exception as e:
        # 保存失败
        db.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片保存失败")

    avatar_url = constants.QINNIU_URL + image_name
    print (avatar_url)
    # 保存成功返回前端
    return jsonify(errno=RET.OK, errmsg="上传成功", data={"avatar_url": avatar_url})


@api.route("/users/name", methods=["PUT"])
@login_check
def save_user_name():
    """
    保存用户姓名
    参数：姓名  用户id
    :return:
    """
    # 获取用户姓名, 用户id
    user_dict = request.get_json()
    user_name = user_dict.get("name")
    user_id = g.get("user_id")

    # 校验用户姓名
    if user_name is None:
        return jsonify(errno=RET.PARAMERR, errmsg="用户名不能为空")

    # 将用户名保存到数据库中
    try:
        User.query.filter_by(id=user_id).update({"name": user_name})
        db.session.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存用户名出错")
    # 修改session中的内容
    session["name"] = user_name

    # 返回
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"name": user_name})


@api.route("/user/info", methods=["GET"])
@login_check
def get_user_info():
    """获取用户信息"""
    user_id = g.get("user_id")
    # 获取用户对象
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")
    user_dict = {
        "name": user.name,
        "mobile": user.mobile,
        "avatar_url": constants.QINNIU_URL + user.avatar_url
    }
    return jsonify(errno=RET.OK, errmsg="获取成功", data=user_dict)


@api.route("/user/auth", methods=["GET"])
@login_check
def get_auth_info():
    """获取验证信息"""
    # 获取用户id
    user_id = g.get("user_id")

    # 获取用户
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 判断是否有过实名认证
    # if user.id_card is None:
    #     return jsonify(errno=RET.NODATA, errmsg="用户还没有实名认证")
    return jsonify(errno=RET.OK, errmsg="获取成功", data={"id_card": user.id_card, "real_name": user.real_name})


@api.route("/user/auth", methods=["POST"])
@login_check
def to_auth():
    """实名认证"""
    # 获取用户信息
    user_dict = request.get_json()
    id_card = user_dict.get("id_card")
    real_name = user_dict.get("real_name")
    user_id = g.get("user_id")

    # 校验信息
    if not all([id_card, real_name]):
        return jsonify(errno=RET.PARAMERR, errmsg="数据不完整")

    # 保存信息
    try:
        User.query.filter_by(id=user_id).update({"real_name":real_name, "id_card":id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据错误")

    return jsonify(errno=RET.OK, errmsg="实名认证成功")
