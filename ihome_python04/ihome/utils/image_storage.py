# -*- coding: utf-8 -*-

from qiniu import Auth, put_data, etag
import qiniu.config


# 需要填写你的 Access Key 和 Secret Key
access_key = 'XSLTm1IGKR51kW5Et7atUtWjAUaXrYeMzYrAces8'
secret_key = 'utzOgT88lDgbJRtSDhf7xZwt5ufIlgRZDVdjT13K'


def storage(data_file):
    """
    上传文件到七牛
    :param data_file: 要上传的文件数据
    :return:
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome-zhanglei'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, data_file)
    # print(info)
    # print("*"*10)
    # print(ret)
    if info.status_code == 200:
        return ret.get("key")
    else:
        raise Exception("保存失败")


if __name__ == '__main__':
    with open("./1.jpg", "rb") as f:
        data_file = f.read()
        # print (data_file)
        storage(data_file)


