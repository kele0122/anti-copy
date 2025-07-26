import numpy as np
import cv2

def compute_ring_energy(image, inner_radius_ratio=0.05, outer_radius_ratio=0.2, visualize=True):
    """
    计算傅立叶频谱环形区域的能量（内圈和外圈半径自适应图像尺寸）
    :param image_path: 输入图像路径
    :param inner_radius_ratio: 内圈半径比例（相对于图像最小边）
    :param outer_radius_ratio: 外圈半径比例（相对于图像最小边）
    :param visualize: 是否可视化频谱和环形区域
    :return: 环形区域能量, 总能量, 能量占比, 判断结果
    """
    rows, cols = image.shape

    # 取左边 10%-50% 的宽度范围
    left_start = int(cols * 0.10)  # 左边10%
    left_end = int(cols * 0.5)  # 左边50%
    left_half = image[:, left_start:left_end]  # 宽度方向裁剪

    # 上下各去掉10%（即保留中间80%的高度）
    height = left_half.shape[0]
    top_cut = int(height * 0.1)  # 上边10%
    bottom_cut = int(height * 0.9)  # 下边10%（即保留到90%的位置）
    cropped_image = left_half[top_cut:bottom_cut, :]

    # 更新 image
    image = cropped_image
    rows, cols = image.shape  # 更新尺寸

    # # 显示图像
    # cv2.imshow("Cropped Image", cropped_image)
    # cv2.waitKey(0)  # 按任意键关闭窗口
    # cv2.destroyAllWindows()

    # 2. 傅立叶变换并移到中心
    dft = np.fft.fft2(image)
    dft_shift = np.fft.fftshift(dft)
    spectrum = np.abs(dft_shift)  # 幅度谱

    # 3. 计算自适应环形半径
    min_edge = min(rows, cols)
    inner_radius = int(inner_radius_ratio * min_edge)
    outer_radius = int(outer_radius_ratio * min_edge)
    cx, cy = cols // 2, rows // 2

    # 4. 创建环形掩模（外圈内非内圈的区域）
    y, x = np.ogrid[:rows, :cols]
    dist_from_center = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    ring_mask = (dist_from_center <= outer_radius) & (dist_from_center > inner_radius)

    # 5. 计算能量（幅度平方和）
    ring_energy = np.sum(spectrum[ring_mask] ** 2)
    total_energy = np.sum(spectrum ** 2)
    energy_ratio = ring_energy / total_energy

    # 6. 根据能量占比进行判断
    if energy_ratio < 0.007:  # 0.7%
        judgment = 201 # 真
    elif energy_ratio > 0.05:  # 5%
        judgment = 202 # 假
    else:
        judgment = 203 #不确定

    return ring_energy, total_energy, energy_ratio, judgment


def judge_halftone(image):

    ring_energy, total_energy, ratio, judgment = compute_ring_energy(
        image,
        inner_radius_ratio=0.01,
        outer_radius_ratio=0.03
    )

    print(f"""环形区域能量: {ring_energy:.2f} 总能量: {total_energy:.2f} 能量占比: {ratio:.2%} 判断结果: {judgment}""")