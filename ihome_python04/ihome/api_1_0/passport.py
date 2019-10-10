# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db, constants
from ihome.models import User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import re


@api.route("/users", methods=["POST"])
def register():
    """注册
    请求的参数： 手机号、短信验证码、密码、确认密码
    参数格式：json
    """
    # 获取请求的json数据，返回字典
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 判断用户的手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # else:
    #     if user is not None:
    #         # 表示手机号已存在
    #         return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 盐值   salt

    #  注册
    #  用户1   password="123456" + "abc"   sha1   abc$hxosifodfdoshfosdhfso
    #  用户2   password="123456" + "def"   sha1   def$dfhsoicoshdoshfosidfs
    #
    # 用户登录  password ="123456"  "abc"  sha256      sha1   hxosufodsofdihsofho

    # 保存用户的注册数据到数据库中
    user = User(name=mobile, mobile=mobile)
    # user.generate_password_hash(password)

    user.password = password  # 设置属性

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚
        db.session.rollback()
        # 表示手机号出现了重复值，即手机号已注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        # 表示手机号出现了重复值，即手机号已注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


# /login
# post
@api.route("/session", methods=["POST"])
def login():
    """登陆操作
    参数：手机号， 密码
    参数类型：json
    请求方式：post
    """
    # 获取参数
    user_dict = request.get_json()
    mobile = user_dict.get("mobile")
    password = user_dict.get("password")
    # 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验手机号
    if not re.match(r'1[34579]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号不正确")

    # 判断用户登陆请求是否过多
    # redis记录  "redis_num_ip": "次数"
    user_ip = request.remote_addr
    # 从redis中获取请求次数
    try:
        login_num = redis_store.get("redis_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if login_num is not None and login_num > constants.LOGIN_MAX_TIME:
            return jsonify(errno=RET.REQERR, errmsg="请求次数过多，请稍后再登陆")

    # 逻辑处理
    # 判断用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 判断密码是否一致
    if user is None or not user.check_password(password):
        # 如果验证失败记录验证次数信息，返回
        try:
            redis_store.incr("redis_num_%s" % user_ip)
            redis_store.expire("redis_num_%s" % user_ip, constants.LOGIN_FORBIDEN_TIEM)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.USERERR, errmsg="请输入正确的账户密码")

    # 密码一致，登陆成功
    # 设置登陆状态
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    # 返回
    return jsonify(errno=RET.OK, errmsg="登陆成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检测是否登陆"""
    # 获取session中的名字
    name = session.get("name")

    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """用户退出登陆"""
    # 清除数据
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="ok")