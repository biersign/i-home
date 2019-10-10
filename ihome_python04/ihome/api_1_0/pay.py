# coding:utf-8


from . import api
from flask import current_app, g, jsonify, request
from ihome.utils.commons import login_check
from ihome.utils.response_code import RET
from ihome.models import Order
from alipay import AliPay
from ihome import constants, db
import os


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_check
def to_alipay(order_id):
    """发起支付宝支付"""
    # 获取用户id
    user_id = g.user_id
    # 校验订单
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单不存在")

    # 创建支付宝支付对象
    alipay = AliPay(
        appid="2016101300676658",
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # 手机网站支付，需要跳转到
    # https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单id
        total_amount=str(order.amount/100.0),  # 订单金额
        subject=u"爱家租房 %s " % order.id,   # 订单标题
        return_url="https://127.0.0.1:5000/orders.html",   # 返回的url地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 拼接支付宝网址
    alipay_url = constants.ALIPAY_URL + order_string
    return jsonify(errno=RET.OK, errmsg="ok", data={"pay_url": alipay_url})


@api.route("/order/payment", methods=["PUT"])
def order_check():
    """校验支付是否完成"""
    # 获取数据
    alipay_data = request.form.to_dict()
    signure = alipay_data.pop("sign")

    # 创建支付宝支付对象
    alipay = AliPay(
        appid="2016101300676658",
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    result = alipay.verify(alipay_data, signure)
    if result:
        # 交易成功,更新数据库数据
        id = alipay_data.get("out_trad_on")
        alipay_on = alipay_data.get("trad_on")
        try:
            Order.query.filter_by(id=id).update({"status": "PAID", "alipay_on": alipay_data})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="ok")
