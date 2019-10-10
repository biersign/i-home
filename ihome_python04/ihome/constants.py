# coding:utf-8


# 图片验证码的redis有效期, 单位：秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码的redis有效期, 单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔, 单位：秒
SEND_SMS_CODE_INTERVAL = 60

# 最大登陆请求次数
LOGIN_MAX_TIME = 5

# 登陆错误限制的时间按
LOGIN_FORBIDEN_TIEM = 600

# 七牛链接
QINNIU_URL = "http://pydiyjpqt.bkt.clouddn.com/"

# 地区信息缓存保存时间
REDIS_AREAINFO_CATCH_TIME = 7200

HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS =10

# 房屋详细信息保存时间按
HOUSE_DETAIL_SAVE_TIME = 30

# 首页显示房屋条数
INDEX_MAX_AMOUNT = 5

# 首页缓存保存时间
INDEX_HOUSE_SAVE_TIME = 30

# 列表页每页显示的条数
HOUSES_PERPAGE = 2

# 列表页数据缓存的时间按
HOUSES_LIST_REDIS_TIME = 360

# 支付宝支付网址
ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do?"