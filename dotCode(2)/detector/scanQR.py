# from qreader import QReader
import cv2
import numpy as np

"""
接收：原始二维码照片
过程：对二维码预处理
返回：二维码的解码信息、预处理后的透视变换灰度图
"""

def process_image(image, output_path, qreader, img_size):
    """
    检测并矫正二维码图像，返回解码内容
    :param image_path: 输入图像路径
    :param output_path: 矫正后图像的保存路径
    :return: 成功返回解码文本，失败返回None
    """
    
    texts, detections = qreader.detect_and_decode(image=image, return_detections=True) # 检测并解码二维码
    
    # 验证检测结果
    if not texts or not texts[0] or not detections:
        return None
    
    # 提取二维码信息
    decoded_text = texts[0]
    detection = detections[0]
    
    # 执行透视变换
    src_points = detection['quad_xy'].astype(np.float32) # 提取原始四角坐标（使用quad_xy）
    print("src_points:", src_points)
    dst_points = np.array([
        [1514, 97],    # 左上角
        [2723, 97],   # 右上角
        [2723, 1306],  # 右下角
        [1514, 1306]    # 左下角
    ], dtype=np.float32)
    
    matrix = cv2.getPerspectiveTransform(src_points, dst_points) # 计算透视变换矩阵
    warped = cv2.warpPerspective(image, matrix, (2834, 1417), flags=cv2.INTER_CUBIC)  # 改用立方插值提升图像清晰度
    warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY) # 转换为灰度图

    # # 在保存前添加锐化处理
    # kernel = np.array([[0, -1, 0],
    #                 [-1, 5,-1],
    #                 [0, -1, 0]])
    # mask_gray = cv2.filter2D(mask_gray, -1, kernel)

    cv2.imwrite(output_path, warped_gray)
    return decoded_text, warped_gray, matrix

def scan_qrcode(image, output_preprocess, qreader, img_size):

    """
    得到二维码的字符串信息和正规化的二维码灰度图像
    """
    decoded_text, qr_gray, matrix = process_image(image, output_preprocess, qreader, img_size)

    if decoded_text:
        print(f"二维码识别成功！内容：{decoded_text}")
    else:
        print("未识别到有效二维码")
    
    return decoded_text, qr_gray, matrix