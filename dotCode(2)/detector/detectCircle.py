import os
os.environ["OMP_NUM_THREADS"] = "1"
import cv2
import numpy as np
from sklearn.cluster import KMeans

def process_img(gray_img, output_binary):
    # 计算图像的平均灰度值
    mean_val = np.mean(gray_img)
    # 使用平均灰度值作为阈值进行二值化
    _, binary_img = cv2.threshold(gray_img, mean_val, 255, cv2.THRESH_BINARY)

    cv2.imwrite(output_binary, binary_img)

    return binary_img

def detect_circles(gray_img_origin, binary_img, output_tagImg):
    # 缩小图片，3倍
    binary_img = cv2.resize(binary_img, (gray_img_origin.shape[1] // 3, gray_img_origin.shape[0] // 3))

    h, w = binary_img.shape
    radius = 36

    # 1. 创建一个圆形的结构元素 (kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))

    # 2. 对二值图像进行腐蚀操作
    # 腐蚀后的图像中，像素值为255的点，表示其周围半径为40的区域内所有像素都为255
    eroded_img = cv2.erode(binary_img, kernel)

    # 3. 在指定的中心区域内查找有效圆心
    start_x = radius
    start_y = radius
    end_x = w - radius
    end_y = h - radius

    # 截取中心区域进行查找
    center_region = eroded_img[start_y:end_y, start_x:end_x]
    
    # 找到所有白色像素（有效圆心）的坐标
    # np.argwhere会返回(row, col)对，即(y, x)
    valid_centers_relative = np.argwhere(center_region == 255)

    # 将相对坐标转换回原始图像的绝对坐标
    # argwhere返回的是(y, x)，转换为(x, y)格式
    centers = [(x + start_x, y + start_y) for y, x in valid_centers_relative]

    final_centers = []
    if len(centers) > 5:
        # 使用K-Means聚类将中心点合并为5个
        kmeans = KMeans(n_clusters=5, random_state=0, n_init='auto').fit(centers)
        final_centers = kmeans.cluster_centers_.astype(int).tolist()
    elif len(centers) > 0:
        final_centers = centers
    else:
        # 如果没有找到中心，则返回空列表
        final_centers = []

    result_centers = []

    # 在gray_img_origin上绘制最终的圆
    for center in final_centers:
        # KMeans返回的中心点可能是浮点数，转换为整数
        int_center = tuple(map(int, center))
        # 创建一个新的元组，其中每个元素都是原坐标乘以3
        scaled_center = tuple(coord * 3 for coord in int_center)
        result_centers.append(scaled_center)
        # 使用放大后的坐标和半径来绘制圆
        cv2.circle(gray_img_origin, scaled_center, radius * 3, (0, 255, 0), 2)

    cv2.imwrite(output_tagImg, gray_img_origin)
    return result_centers

def det_circle(gray_img, output_binary, output_tagImg):
    circle_centers = []
    gray_img = gray_img[:, :gray_img.shape[1] // 2]
    print("gray_img.shape:", gray_img.shape)
    gray_img_origin = gray_img.copy()

    binary_img = process_img(gray_img, output_binary)
    
    # 检测圆并在output_tagImg上标记
    circle_centers = detect_circles(gray_img_origin, binary_img, output_tagImg)
    
    return circle_centers
