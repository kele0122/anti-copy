import numpy as np
import math
import hashlib
import random

def get_square_centers(vertical, horizontal, patch = None):

   edge_length = (vertical + horizontal) // 9

   vertical_centers = [int(vertical * 1/5), int(vertical * 1/2), int(vertical * 4/5)]
   horizontal_centers = [int(horizontal * 1/8), int(horizontal * 3/8), int(horizontal * 5/8), int(horizontal * 7/8)]
    
   # half_edge = edge_length // 2

   # for vc in vertical_centers:
   #    for hc in horizontal_centers:
   #       # 计算正方形的起始坐标 (左上角)
   #       start_row = vc - half_edge
   #       start_col = hc - half_edge

   #       # 确定实际绘制区域，防止超出图像边界
   #       y_start = max(0, start_row)
   #       y_end = min(vertical, start_row + edge_length)
   #       x_start = max(0, start_col)
   #       x_end = min(horizontal, start_col + edge_length)

   #       # 绘制正方形 (使用白色 255)
   #       patch[y_start, x_start:x_end] = 0
   #       patch[y_end-1, x_start:x_end] = 0
   #       patch[y_start:y_end, x_start] = 0
   #       patch[y_start:y_end, x_end-1] = 0

   return vertical_centers, horizontal_centers, edge_length

def get_positions(data):
   # 将字符串转换为位置坐标
   hash_bytes = hashlib.sha256(data.encode()).digest()[:4]
   hash_int = int.from_bytes(hash_bytes, byteorder='big')
   mixed = (hash_int & 0xFFFF) ^ ((hash_int >> 16) & 0xFFFF)  # 高低16位异或

   n=12
   k=5
   comb_num = math.comb(n, k)
   index = mixed % comb_num 
   
   combination = []
   pos = 0
   remaining = n
   need = k
   for i in range(n):
      # 计算跳过当前位的组合数
      c = math.comb(remaining-1, need-1)
      if index >= c: # 不选当前位，索引值减少
         index -= c
      else: # 选中当前位，减少需求数量
         combination.append(pos)
         need -= 1
         if need == 0:
            break  # 提前终止
      # 移动检测位置
      pos += 1
      remaining -= 1

   print("combination: ", combination)
   
   return combination

def get_circle_centers(circle_radius, selected_positions, vertical_centers, horizontal_centers, edge_length, vertical, horizontal):
   centers = []
   half_edge = edge_length // 2

   # 首先，创建一个所有8个方形中心坐标的有序列表，以便通过索引访问
   # 顺序为：(v0,h0), (v0,h1), (v0,h2), (v0,h3), (v1,h0), ...
   all_square_centers = []
   for vc in vertical_centers:
      for hc in horizontal_centers:
         all_square_centers.append((vc, hc)) # (y, x) 坐标

   # 按照 selected_positions 的顺序处理每个需要放置圆的方形
   for square_index in selected_positions:
      # 获取当前方形的中心坐标
      square_center_y, square_center_x = all_square_centers[square_index]

      # 定义当前方形的边界
      min_y = square_center_y - half_edge
      max_y = square_center_y + half_edge
      min_x = square_center_x - half_edge
      max_x = square_center_x + half_edge

      # 循环直到为当前方形找到一个不重叠的圆心位置
      while True:
         # 在方形边界内随机生成一个新圆心
         new_center_y = random.randint(min_y, max_y)
         new_center_x = random.randint(min_x, max_x)
         new_center = (new_center_y, new_center_x)

         # 1. 边界检查：确保整个圆都在图像内
         if (new_center_y - circle_radius < 0 or
            new_center_y + circle_radius > vertical or
            new_center_x - circle_radius < 0 or
            new_center_x + circle_radius > horizontal):
            continue  # 如果圆超出边界，则重新生成

         # 2. 重叠检查：检查新生成的圆是否与已存在的圆重叠
         is_overlapping = False
         for existing_center in centers:
               # 计算新圆心与已存在圆心之间的距离
               distance = math.hypot(new_center[1] - existing_center[1], new_center[0] - existing_center[0])
               
               # 如果距离小于两倍半径，则表示两个圆相交
               if distance < 2 * circle_radius:
                  is_overlapping = True
                  break  # 发生重叠，跳出检查，重新生成
         
         # 如果没有发生重叠，则该圆心有效
         if not is_overlapping:
               centers.append(new_center)
               break  # 圆心有效，跳出while循环，处理下一个方形

   return centers

def draw_circles(circle_centers, circle_radius, patch):
   for center_y, center_x in circle_centers:
      y_start = int(center_y - circle_radius)
      y_end = int(center_y + circle_radius + 1)
      x_start = int(center_x - circle_radius)
      x_end = int(center_x + circle_radius + 1)

      # 仅在边界框内创建坐标网格
      yy, xx = np.mgrid[y_start:y_end, x_start:x_end]

      # 计算到圆心的距离的平方
      dist_sq = (yy - center_y)**2 + (xx - center_x)**2

      # 创建一个布尔掩码，其中圆内的像素为True
      mask = dist_sq <= circle_radius**2
      
      # 使用掩码将边界框内对应圆的区域设置为255（白色）
      patch[y_start:y_end, x_start:x_end][mask] = 255

   return patch

def process_patch(data, patch = None):
   vertical = patch.shape[0]
   horizontal = patch.shape[1]

   vertical_centers, horizontal_centers, edge_length = get_square_centers(vertical, horizontal, patch)
   square_index = get_positions(data)
   circle_radius = edge_length // 2.5
   print("circle_radius:", circle_radius)
   circle_centers = get_circle_centers(circle_radius, square_index, vertical_centers, horizontal_centers, edge_length, vertical, horizontal)
   circle_patch = draw_circles(circle_centers, circle_radius, patch)

   return circle_patch