import json
from generator.gen_qr import (
    generate_random_string,
    generate_qr,
    convert_dpi
)
from generator import gen_patch28
from generator import gen_patch11
from generator import gen_circle

"""
生成一个二维码
"""

if __name__ == '__main__':
    with open('./setting.json', 'r') as file:
        params = json.load(file)
    
    generate_params = params['generate']
    dpi = generate_params['dpi']
    
    random_info = generate_random_string(10)

    qr_img = generate_qr(
        data=random_info,
        level=generate_params['level'],
        version=generate_params['version'],
        box_size=generate_params['box_size'],
        outer_border=generate_params['outer_border']
    )

    patch, qr_img = gen_patch11.process_qr(
        qr_img = qr_img,
        dpi = dpi,
    )

    circle_patch = gen_circle.process_patch(
        data = random_info,
        patch = patch
    )

    img = gen_patch11.combine_images(
        qr_img = qr_img,
        halftone_img = circle_patch
    )
    
    convert_dpi(img, dpi, f'./gen_img/img_{dpi}.tiff')