import numpy as np
import random
from PIL import Image, ImageDraw
import math


def generate_poisson_disc_samples(width, height, sampling_radius, k=20):
    """使用Poisson-disk采样生成点集"""

    def point_valid(point, grid, grid_width, grid_height, sampling_radius, cell_size):
        gx, gy = int(point[0] // cell_size), int(point[1] // cell_size)
        for x in range(max(0, gx - 6), min(gx + 6, grid_width)):
            for y in range(max(0, gy - 6), min(gy + 6, grid_height)):
                if grid[x][y] is not None:
                    dist = math.hypot(point[0] - grid[x][y][0], point[1] - grid[x][y][1])
                    if dist < sampling_radius:
                        return False
        return True

    cell_size = sampling_radius / math.sqrt(2)
    grid_width = int(math.ceil(width / cell_size))
    grid_height = int(math.ceil(height / cell_size))
    grid = [[None for _ in range(grid_height)] for _ in range(grid_width)]

    process_list = []
    sample_points = []

    first_point = (random.uniform(0, width), random.uniform(0, height))
    process_list.append(first_point)
    sample_points.append(first_point)
    gx, gy = int(first_point[0] // cell_size), int(first_point[1] // cell_size)
    grid[gx][gy] = first_point

    while process_list:
        point = process_list.pop(random.randint(0, len(process_list) - 1))
        for _ in range(k):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(sampling_radius, 2 * sampling_radius)
            new_point = (
                point[0] + radius * math.cos(angle),
                point[1] + radius * math.sin(angle)
            )
            if 0 <= new_point[0] < width and 0 <= new_point[1] < height:
                if point_valid(new_point, grid, grid_width, grid_height, sampling_radius, cell_size):
                    process_list.append(new_point)
                    sample_points.append(new_point)
                    gx, gy = int(new_point[0] // cell_size), int(new_point[1] // cell_size)
                    grid[gx][gy] = new_point
    return sample_points


def create_halftone_with_qr(qr_img, dpi=2400, height_cm=1.5):
    """
    创建半色调点矢量图并与二维码拼接

    参数:
    - output_path: 输出文件路径
    - qr_path: 二维码图片路径
    - height_cm: 图像高度(厘米)，二维码将与此高度相同
    - dpi: 分辨率(每英寸点数)
    """
    # 设置宽高比：半色调部分宽度是高度的2倍，二维码是正方形(高度x高度)
    halftone_width_cm = height_cm * 1  # 半色调区域宽度
    qr_width_cm = height_cm  # 二维码区域宽度(与高度相同)
    total_width_cm = halftone_width_cm + qr_width_cm  # 总宽度

    # 转换单位
    inches_per_cm = 0.393701
    height_inch = height_cm * inches_per_cm
    halftone_width_inch = halftone_width_cm * inches_per_cm
    qr_width_inch = qr_width_cm * inches_per_cm

    # 计算像素尺寸
    height_px = int(height_inch * dpi)
    halftone_width_px = int(halftone_width_inch * dpi)
    qr_width_px = int(qr_width_inch * dpi)
    total_width_px = halftone_width_px + qr_width_px

    # 参数设置
    sampling_radius = 12  # 泊松盘半径12像素

    # 生成泊松盘采样点
    points = generate_poisson_disc_samples(halftone_width_px, height_px, sampling_radius)

    # 创建半色调图像
    halftone_img = Image.new("1", (halftone_width_px, height_px), 1)  # 1-bit image, white background
    draw = ImageDraw.Draw(halftone_img)

    # 绘制一种点
    dot_radius = 4  # 点半径4像素
    for (x, y) in points:
        draw.ellipse([x - dot_radius, y - dot_radius,
                      x + dot_radius, y + dot_radius], fill=0)

    # 绘制所有点，50%半径为3像素，50%半径为4像素
    # for (x, y) in points:
    #     # 随机选择点半径
    #     dot_radius = 5 if random.random() > 0.7 else 3
    #     draw.ellipse([x - dot_radius, y - dot_radius,
    #                   x + dot_radius, y + dot_radius], fill=0)

    # for (x, y) in points:
    #     # 随机选择点半径（3px、4px或5px）
    #     rand_val = random.random()
    #     if rand_val < 0.25:  # 50%概率为3px
    #         dot_radius = 3
    #     elif rand_val < 0.75:  # 30%概率为4px (0.8-0.5=0.3)
    #         dot_radius = 4
    #     else:  # 20%概率为5px (1.0-0.8=0.2)
    #         dot_radius = 5
    #
    #     draw.ellipse([x - dot_radius, y - dot_radius,
    #                   x + dot_radius, y + dot_radius], fill=0)
        
    qr_img = qr_img.resize((qr_width_px, height_px), Image.LANCZOS)

    return halftone_img, qr_img


def combine_images(qr_img, halftone_img):
    halftone_img =  Image.fromarray(halftone_img)
    """将二维码和半色调图像组合在一起"""
    total_width_px = qr_img.size[0] + halftone_img.size[0]
    height_px = max(qr_img.size[1], halftone_img.size[1])
    halftone_width_px = halftone_img.size[0]

    # 创建组合图像
    combined_img = Image.new("1", (total_width_px, height_px), 1)
    combined_img.paste(halftone_img, (0, 0))
    combined_img.paste(qr_img, (halftone_width_px, 0))

    return combined_img

# 使用示例
def process_qr(qr_img = None, dpi = 2400):

    halftone_img, qr_img = create_halftone_with_qr(qr_img, dpi, height_cm=1)

    return np.array(halftone_img), qr_img