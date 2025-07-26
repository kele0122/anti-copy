import cv2
import numpy as np

def trans_index(points, M):
    """
    将变换后的坐标点还原为原始坐标点
    :param points: 变换后的坐标点列表，例如 [[x1, y1], [x2, y2], ...]
    :param M: 原始的透视变换矩阵
    :return: 还原后的坐标点列表
    """
    try:
        M_inv = np.linalg.inv(M)
    except np.linalg.LinAlgError:
        print("矩阵是奇异的，无法计算逆矩阵。")
        return None

    points_np = np.array([points], dtype='float32')
    original_points = cv2.perspectiveTransform(points_np, M_inv)

    if original_points is None:
        return None

    return original_points[0]

def draw_transformed_circles(image, transformed_centers, transformed_radius, matrix):
    """
    将变换后图像上的圆，根据逆透视变换绘制到原始图像上。
    """
    if transformed_centers is None:
        return

    for center in transformed_centers:
        # 定义圆心和圆周上的四个点（上、下、左、右）
        points_to_transform = [
            center,
            [center[0], center[1] - transformed_radius],  # Top
            [center[0], center[1] + transformed_radius],  # Bottom
            [center[0] - transformed_radius, center[1]],  # Left
            [center[0] + transformed_radius, center[1]]   # Right
        ]

        # 将这些点变换回原始图像坐标系
        original_points = trans_index(points_to_transform, matrix)

        if original_points is not None and len(original_points) == 5:
            original_center = tuple(map(int, original_points[0]))
            
            # 计算还原后的点到新圆心的平均距离作为新半径
            radii = [np.linalg.norm(np.array(original_center) - np.array(p)) for p in original_points[1:]]
            original_radius = int(np.mean(radii))

            # 在原始图像上绘制圆
            cv2.circle(image, original_center, original_radius, (0, 0, 255), 5) # 红色圆圈，线宽为5

def gen_tagimg(image, circle_centers, matrix, output_result):
    transformed_radius = 36 * 3
    draw_transformed_circles(image, circle_centers, transformed_radius, matrix)
 
    cv2.imwrite(output_result, image)

    return image