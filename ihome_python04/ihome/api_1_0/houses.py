# coding: utf-8

from . import api
from ihome.utils.commons import login_check
from flask import g, current_app, jsonify, request, session
from ihome import db, redis_store
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome import constants
from ihome.models import Area, House, Facility, HouseImage, User, Order
from ihome.utils.commons import login_check
from datetime import datetime
import json


@api.route("/areas")
def get_area_info():
    """获取房屋地区信息"""
    # 从缓存中获取数据
    try:
        json_dict = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if json_dict is not None:
            # 缓存中有数据
            current_app.logger.info(" hit redis area_info ")
            return json_dict, 200, {"Content-Type": "application/json"}

    # 从数据库中获取房屋信息
    try:
        area_list = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="获取房屋信息失败")

    # 将房屋信息转换为字典，重新拼接列表
    area_list_to = []
    for area in area_list:
        area_list_to.append(area.to_dict())
    # 将数据转换为json字符串
    resp_dict = dict(errno=RET.OK, errmsg="ok", data=area_list_to)
    json_dict = json.dumps(resp_dict)
    # 将房屋信息保存在缓存中
    try:
        redis_store.setex("area_info",constants.REDIS_AREAINFO_CATCH_TIME, json_dict)
    except Exception as e:
        current_app.logger.error(e)

    # 返回
    return json_dict, 200, {"Content-Type": "application/json"}


@api.route("/houses/info", methods=["POST"])
@login_check
def save_house_info():
    """
    保存房屋信息
    area_id:""
    title:""
    price:""
    address:""
    room_count:""
    acreage:""
    unit:""
    capacity:""
    beds:""
    deposit:""
    min_days:""
    max_days:""
    :return:
    """
    # 获取房屋基本信息
    house_data = request.get_json()
    user_id = g.get("user_id")
    area_id = house_data.get("area_id")
    title = house_data.get("title")
    price = house_data.get("price")
    address = house_data.get("address")
    room_count = house_data.get("room_count")
    acreage = house_data.get("acreage")
    unit = house_data.get("unit")
    capacity = house_data.get("capacity")
    beds = house_data.get("beds")
    deposit = house_data.get("deposit")
    min_days = house_data.get("min_days")
    max_days = house_data.get("max_days")

    # 数据校验
    if not all([user_id, area_id, title, price, address,
                room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="数据不完整")

    # 地区id校验
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")
    else:
        if not area:
            return jsonify(errno=RET.NODATA, errmsg="地区不存在")

    # 金额检查
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg="价格数据错误")

    # 生成房屋对象
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 获取房屋设备信息数据
    facilities_ids = house_data.get("facilities")
    # 对房屋设备信息数据校验
    if facilities_ids:
        # 有房屋设备信息
        try:
            facilities_ids = Facility.query.filter(Facility.id.in_(facilities_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="设备信息数据库出错")

        if facilities_ids:
            # 表示有合法的设备信息
            house.facilities = facilities_ids

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据库信息出错")
    # 成功返回
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST"])
@login_check
def save_house_image():
    """保存房屋图片
    参数： 图片， 房屋id
    """
    # 获取参数
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    # 校验参数
    if not([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验房屋id
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    image_data = image_file.read()
    if house:
        # 房屋真实存在
        try:
            file_name = storage(image_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="第三方错误")

    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)
    # 判断房屋首页图片是否存在
    if house.index_image_url is None:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存到数据库失败")
    image_url = constants.QINNIU_URL + file_name
    # 成功返回
    return jsonify(errno=RET.OK, errmsg="ok", data={"image_url": image_url})


@api.route("/houses/user", methods=["GET"])
@login_check
def get_user_houses():
    """获取当前用户的房源"""
    # 获取当前用户的id
    user_id = g.get("user_id")

    # 获取当前用户的房源
    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据库数据异常")

    house_dict = []
    if houses:
        for house in houses:
            house_dict.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg="获取成功", data={"house_dict": house_dict})


@api.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋详情"""
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数确实")

    # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info("hit house info redis")
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, ret), \
               200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转换为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")

    # 存入到redis中
    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, json_house), \
           200, {"Content-Type": "application/json"}
    return resp


@api.route("/house/index", methods=["GET"])
def get_house_index():
    """获取首页房屋信息"""
    # 从缓存中获取首页房屋信息
    try:
        json_dict = redis_store.get("index_house")
    except Exception as e:
        current_app.logger.error(e)

    if json_dict:
        return json_dict, 200, {"Content-Type": "application/json"}

    try:
        houses = House.query.order_by(House.order_count.desc()).limit(constants.INDEX_MAX_AMOUNT)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    house_list = []
    for house in houses:
        if not house.index_image_url:
            continue
        house_list.append(house.to_basic_dict())

    house_dict = dict(errno=RET.OK, errmsg="获取数据成功", data=house_list)
    json_dict = json.dumps(house_dict)

    # 将首页信息保存到缓存中
    try:
        redis_store.setex("index_house", constants.INDEX_HOUSE_SAVE_TIME, json_dict)
    except Exception as e:
        current_app.looger.error(e)

    return json_dict, 200, {"Content-Type": "application/json"}


# /api/v1.0/houses?sd=2018-12-12&ed=2018-12-15&aid=2&sk=new&p=1
@api.route("/houses")
def get_houses_list():
    """获取房屋列表页(搜索页)"""
    # 获取参数
    start_date = request.args.get("sd", "")  # 开始日期
    end_date = request.args.get("ed", "")    # 结束日期
    area_id = request.args.get("aid", "")    # 区域日期
    sort_key = request.args.get("sk", default="new")    # 搜索关键字
    page = request.args.get("p")         # 当前页数

    # 校验时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期格式不对")

    # 区域校验
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="地区不存在")

    # 页数校验
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 获取redis中的数据
    redis_key = "house_list_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}

    # 定义与预定时间冲突的订单列表
    conflict_orders = None
    # 定义数据库查询顾虑条件列表
    param_list = []
    #  数据库中获取冲突的订单
    try:
        if start_date and end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询订单错误")

    if conflict_orders:
        # 从定单中获取冲突房屋的id
        conflict_id = [order.house_id for order in conflict_orders]

        # 如果冲突的id不为空拼接到参数列表
        if conflict_id:
            param_list.append(House.id.notin_(conflict_id))

    if area_id:
        param_list.append(House.area_id == area_id)

    # 获取分页搜索集
    if sort_key == "booking":      # 订单倒序排列
        houses_query = House.query.filter(*param_list).order_by(House.order_count.desc())
    elif sort_key == "price-inc":  # 价格由低到高
        houses_query = House.query.filter(*param_list).order_by(House.price.asc())
    elif sort_key == "price-des":  # 价格由高到低
        houses_query = House.query.filter(*param_list).order_by(House.price.desc())
    else:                          # 时间倒序
        houses_query = House.query.filter(*param_list).order_by(House.create_time.desc())

    # 获取查询集的分页对象
    try:
        #                                 当前页数              分页每页条数                         错误显示
        house_obj = houses_query.paginate(page=page, per_page=constants.HOUSES_PERPAGE, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库房屋错误")

    # 分页内容
    houses_li = house_obj.items
    houses = []
    for house in houses_li:
        houses.append(house.to_basic_dict())

    # 分页总条数
    total_page = house_obj.pages
    # 判断是否设置缓存
    if page <= total_page:
        # 设置缓存
        resp_dict = dict(errno=RET.OK, errmsg="获取成功", data={"total_page": total_page, "houses": houses, "current_page": page})
        resp_json = json.dumps(resp_dict)

        redis_key = "house_list_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)

        try:
            redis_store.hset(redis_key, page, resp_json)
            redis_store.expire(redis_key, constants.HOUSES_LIST_REDIS_TIME)
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}