from flask import Flask, request
import json

from io import BytesIO

from PIL import Image

import uuid
import base64

import os

from src import convertPDF2img, toGrayscale, utilities, noiseRemove, toBlackWhite, detectLines, toBoxes


app = Flask(__name__)


@app.route('/multipart/form-data', methods=['POST'])
def convert_pdf_to_image():

    # print(request.data)  # To check what you are sending

    pdf_file_name = request.json['name']
    pdf_encoded_content = request.json['payload']
    # contrast_factor = request.json['contrastFactor']
    apply_noise_reduction = request.json['applyNoiseReduction']
    segmentation_factor = request.json['segmentationFactor']

    in_memory_pdf_file = base64.b64decode(pdf_encoded_content)
    open(pdf_file_name, 'wb').write(in_memory_pdf_file)

    images_uid_prefix = str(uuid.uuid4())
    convertPDF2img.convertToJPG(pdf_file_name, images_uid_prefix)

    image_index = 0
    image_filenames = []
    images_encoded_content = []
    image_to_process_filename = ''
    files = [f for f in os.listdir('./images') if os.path.isfile(f) and f.startswith(images_uid_prefix)]
    for file in files:
        image_index = image_index + 1
        image_filenames.append(file)
        images_encoded_content.append(BytesIO(base64.b64encode(open(file, 'rb').read())))
        if image_index == 1:
            image_to_process_filename = file

    '''
    temporary_grayscale = images_uid_prefix + "_temporary_grayscale.png"
    temporary_contrast = images_uid_prefix + "_temporary_contrast.png"
    temporary_noise = images_uid_prefix + "_temporary_noise.png"
    temporary_black_white = images_uid_prefix + "_temporary_black_white.png"
    temporary_detect_lines = images_uid_prefix + "_temporary_detect_lines.png"
    '''

    temporary_grayscale_image = toGrayscale.ToGrayscale(Image.open(image_to_process_filename))  # grayscale filter

    if apply_noise_reduction:
        temporary_noise_image = noiseRemove.remove_noise(temporary_grayscale_image)             # noise filter
    else:
        temporary_noise_image = temporary_grayscale_image

    temporary_black_white_image = toBlackWhite.ToBlackAndWhite(temporary_noise_image)           # black-white filter

    lines, lines_coordinates = detectLines.DetectLines(temporary_black_white_image, float(segmentation_factor))
    coordinates = toBoxes.fullFlood(lines_coordinates)

    processed_image_payload = base64.b64encode(temporary_black_white_image)

    return_data = {
        'names': image_filenames,
        'payloads': images_encoded_content,
        'pName': image_to_process_filename,
        'pPayload': processed_image_payload,
        'coords': coordinates
    }

    return json.dumps(return_data)


if __name__ == '__main__':
    app.run()
