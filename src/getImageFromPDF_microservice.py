from flask import Flask, request
import json

from io import BytesIO

from PIL import Image

import uuid
import base64

import os

import convertPDF2img, toGrayscale, utilities, noiseRemove, toBlackWhite, detectLines, toBoxes


app = Flask(__name__)


"""The microservice responsable for managing requests regarding getting a PDF and returning the processed images
The microservice recives a name for the PDF, the PDF's payload, and the boolean parameters for applying the noise reduction and the segmentation factor
The microservice reconstructs the PDF localy, and then converts each page of the PDF to a JPG image, with an unique ID in its name.
For the first image, all needed processing is done (segmentationm noise remove - if specified), returning the payload of the
processed image, as well as the coordinates from the segmentation, and the name of the image
For the rest, it returns an array of payloads and names of the images
"""

@app.route('/multipart/form-data', methods=['POST'])
def convert_pdf_to_image():

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
    files = [f for f in os.listdir('./images') if images_uid_prefix in f]
    for file in files:
        image_index = image_index + 1
        image_filenames.append(file)
        images_encoded_content.append((base64.b64encode(open('./images/' + file, 'rb').read())).decode('utf-8'))
        if image_index == 1:
            image_to_process_filename = file

    temporary_black_white_image = images_uid_prefix + "_temporary_black_white.png"
    '''
    temporary_grayscale = images_uid_prefix + "_temporary_grayscale.png"
    temporary_contrast = images_uid_prefix + "_temporary_contrast.png"
    temporary_noise = images_uid_prefix + "_temporary_noise.png"
    temporary_detect_lines = images_uid_prefix + "_temporary_detect_lines.png"
    '''

    temporary_grayscale_image = toGrayscale.ToGrayscale(Image.open('./images/' + image_to_process_filename))  # grayscale filter

    if apply_noise_reduction:
        print("Noise remove, yay!!!!\n\n\n\n\n\n\n\n\n\n\n\n\n")
        temporary_noise_image = noiseRemove.remove_noise(temporary_grayscale_image)             # noise filter
    else:
        temporary_noise_image = temporary_grayscale_image
    
    temporary_black_white_virtual_image = toBlackWhite.ToBlackAndWhite(temporary_noise_image)           # black-white filter

    lines, lines_coordinates = detectLines.DetectLines(temporary_black_white_virtual_image, float(segmentation_factor))
    coordinates = toBoxes.fullFlood(lines_coordinates)

    utilities.ImageToFile(temporary_black_white_virtual_image, './images/' + temporary_black_white_image)
    
    with open('./images/' + temporary_black_white_image, 'rb') as file:
        processed_image_payload  = (base64.b64encode(file.read())).decode('utf-8')
    
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
