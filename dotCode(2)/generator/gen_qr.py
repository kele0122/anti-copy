import random
import string
import numpy as np
import qrcode
from PIL import Image
from PIL import ImageDraw

"""
生成二维码
"""

# 生成长度为 10 的随机字符串
def generate_random_string(length):
    all_characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(all_characters) for i in range(length))
    return random_string

def generate_qr(data, level=qrcode.constants.ERROR_CORRECT_H, version=4, box_size=10, outer_border=6):
    """
    生成二维码
    :param data: 二维码内容
    :param level: 二维码纠错等级
    :param version: 二维码版本
    :param box_size: 二维码每个黑色模块的像素数
    :param outer_border: 二维码白色边框的宽度（单位：模块）
    :return: 二维码的PIL对象
    """
    qr = qrcode.QRCode(version=version, error_correction=level, box_size=box_size, border=outer_border)
    qr.add_data(data)
    qr.make()
    img = qr.make_image().convert('L') # PIL灰度图
    return img

def convert_dpi(image, dpi, out):
    # 将图像转为二值图
    # blackwhite_image = image.convert(mode='1', dither=None)
    save_params = {
        'format': 'tiff',
        "compression": "tiff_lzw",
        "dpi": (dpi, dpi),
    }
    # 保存结果到新的tiff文件中
    image.save(out, **save_params)