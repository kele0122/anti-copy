import json
import cv2

from detector import scanQR, detectCircle, verify_position, result_tagimg, verify_halftone

from qreader import QReader

if __name__ == '__main__':

    with open('./setting.json', 'r') as file:
        params = json.load(file)
    
    generate_params = params['generate']

    # qrcode_size = (21 + (generate_params['version'] - 1) * 4) * generate_params['box_size']
    # img_size = qrcode_size + 2 * generate_params['outer_border'] * generate_params['box_size']
    img_size = 600

    qreader = QReader()

# ------------------------------------------------------------------------------
    input_path = f"det_img/det_img9.jpg"
    output_preprocess = f"det_img/preprocess_img.png"
    output_binary = f"det_img/binary_img.png"
    output_tagImg = f"det_img/tagImg_img.png"
    output_result = f"det_img/result_img.png"

    # 读取图像
    image = cv2.imread(input_path)

    image_cp = image.copy()

    # 识别二维码并对二维码初步调整
    decoded_text, gray_img, matrix = scanQR.scan_qrcode(image_cp, output_preprocess, qreader, img_size)

    # 检测半色调
    halftone_result = verify_halftone.judge_halftone(gray_img)
    print("halftone_result:", halftone_result)

    gray_img_cp = gray_img.copy()
    circle_centers = detectCircle.det_circle(gray_img_cp, output_binary, output_tagImg)

    circle_result = verify_position.judge_position(circle_centers, decoded_text)
    print("circle_result:", circle_result)

    img_result = result_tagimg.gen_tagimg(image, circle_centers, matrix, output_result)