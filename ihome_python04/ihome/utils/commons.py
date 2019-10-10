# coding:utf-8

from werkzeug.routing import BaseConverter
import functools
from flask import session, g, jsonify
from ihome.utils.response_code import RET


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 定义登陆校验装饰器
def login_check(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户登陆状态
        user_id = session.get("user_id")
        if user_id is not None:
            # 用户已经登陆
            # 保存到g对象中
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    return wrapper
