from generator import gen_circle
import numpy as np

def detect_centers(circle_centers):

    vertical = 1417
    horizontal = 1417

    edge_length = (vertical + horizontal) // 9
    half_edge = edge_length // 2

    vertical_centers = [int(vertical * 1/5), int(vertical * 1/2), int(vertical * 4/5)]
    horizontal_centers = [int(horizontal * 1/8), int(horizontal * 3/8), int(horizontal * 5/8), int(horizontal * 7/8)]

    # 创建12个方形区域的中心坐标
    square_centers = []
    for vc in vertical_centers:
        for hc in horizontal_centers:
            square_centers.append((hc, vc)) # (x, y)

    detect_positions = []
    # 遍历每一个检测到的圆心
    for circle_center in circle_centers:
        cx, cy = circle_center
        min_dist = float('inf')
        closest_square_index = -1

        # 遍历12个方形区域，找到距离当前圆心最近的方形
        for i, square_center in enumerate(square_centers):
            sx, sy = square_center
            # 计算距离的平方
            dist_sq = (cx - sx)**2 + (cy - sy)**2
            
            if dist_sq < min_dist:
                min_dist = dist_sq
                closest_square_index = i
        
        detect_positions.append(closest_square_index)

    # 结果排序
    detect_positions.sort()

    return detect_positions

def judge_position(circle_centers, decoded_text):
    real_positions = gen_circle.get_positions(decoded_text)
    print("real_positions:", real_positions)

    detect_positions = detect_centers(circle_centers)
    print("detect_positions:", detect_positions)
    
    if real_positions == detect_positions:
        return 101
    else:
        return 102