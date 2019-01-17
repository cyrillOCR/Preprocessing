import base64
import hashlib
import os
import time
import sys
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import uuid

from src import contrastAdjustor, noiseRemove, detectLines, toGrayscale, toBlackWhite, toBoxes, utilities, resizeImage, \
    dilation, convertPDF2img
from src.utilities import ImageToFile, FileToImage

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return "OMAGA IT WfORKS!"


@app.route('/addImage', methods=['GET'])
def get():
    return "Post only"


@app.route('/addImage', methods=['POST', 'OPTIONS'])
def addImage():
    sys.setrecursionlimit(2000000)
    name = request.json['name']
    payload = request.json['payload']
    contrastFactor = request.json['contrastFactor']
    applyDilation = request.json['applyDilation']
    applyNoiseReduction = request.json['applyNoiseReduction']
    segmentationFactor = request.json['segmentationFactor']
    separationFactor = request.json['separationFactor']
    tempBlackWhite = ''

    print(
        'Received image {}\n\tcontrastFactor:{}\n\tapplyDilation:{}\n\tapplyNoiseReduction:{}\n\tsegmentationFactor:{}\n\tseparationFactor:{}\n\t'.format(
            name, contrastFactor, applyDilation, applyNoiseReduction, segmentationFactor, separationFactor))

    try:

        originalImage = Image.open(BytesIO(base64.b64decode(payload)))

        id = int(round(time.time() * 1000))
        tempBlackWhite = str(id) + "_tempBW.png"

        originalImage = resizeImage.resizeImg(originalImage, 2000, 1900)

        originalImage = toGrayscale.ToGrayscale(originalImage)

        if applyDilation:
            originalImage = dilation.dilation(originalImage)
            originalImage = dilation.erosion(originalImage)

        if applyNoiseReduction:
            absoluteImage = noiseRemove.remove_noise(originalImage)
        else:
            absoluteImage = contrastAdjustor.AdjustContrast(originalImage, float(contrastFactor))
            absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)

        ImageToFile(absoluteImage, tempBlackWhite)

        lines, linesCoord = detectLines.DetectLines(absoluteImage, float(segmentationFactor))

        toBoxes.prepareDebug(tempBlackWhite)  # remove this if you don't want an image with the rectangles
        toBoxes.GetPixels(absoluteImage)
        output = toBoxes.fullFlood(linesCoord, separationFactor)

        newPayload = base64.b64encode(open(tempBlackWhite, "rb").read())

        # cleanup
        if os.path.exists(tempBlackWhite):
            os.remove(tempBlackWhite)
        if os.path.exists("output_image.jpg"):
            os.remove("output_image.jpg")

        data = {
            "name": name,
            "payload": str(newPayload),
            "coords": output
        }
        # return json.dumps(data)
        return jsonify(json.dumps(data)), 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    except Exception as err:
        print("!!!Error: ", err)
        if os.path.exists(tempBlackWhite):
            os.remove(tempBlackWhite)
        if os.path.exists("output_image.jpg"):
            os.remove("output_image.jpg")
        return jsonify(json.dumps(str(err))), 500, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
        }


@app.route('/addPdf', methods=['POST', 'OPTIONS'])
def convert_pdf_to_image():
    sys.setrecursionlimit(2000000)

    pdf_file_name = request.json['name']
    pdf_encoded_content = request.json['payload']
    apply_dilation = request.json['applyDilation']
    contrast_factor = request.json['contrastFactor']
    apply_noise_reduction = request.json['applyNoiseReduction']
    segmentation_factor = request.json['segmentationFactor']
    separation_factor = request.json['separationFactor']

    print(
        'Received pdf {}\n\tcontrastFactor:{}\n\tapplyDilation:{}\n\tapplyNoiseReduction:{}\n\tsegmentationFactor:{}\n\tseparationFactor:{}\n\t'.format(
            pdf_file_name, contrast_factor, apply_dilation, apply_noise_reduction, segmentation_factor,
            separation_factor))

    in_memory_pdf_file = base64.b64decode(pdf_encoded_content)
    open(pdf_file_name, 'wb').write(in_memory_pdf_file)

    images_uid_prefix = str(uuid.uuid4())
    nr_pages = convertPDF2img.convertToJPG(pdf_file_name, images_uid_prefix)

    image_index = 0
    image_filenames = []
    images_encoded_content = []
    image_to_process_filename = ''
    for i in range(1, nr_pages + 1):
        file = './images' + images_uid_prefix + '_' + str(i) + '.jpg'
        print(file)
        image_index = image_index + 1
        image_filenames.append(file)
        images_encoded_content.append((base64.b64encode(open('./images/' + file, 'rb').read())).decode('utf-8'))
        if image_index == 1:
            image_to_process_filename = file
        else:
            # delete temp img
            os.remove('./images/' + file)

    # delete pdf
    os.remove(pdf_file_name)

    temporary_black_white_image = images_uid_prefix + "_temporary_black_white.png"
    '''
    temporary_grayscale = images_uid_prefix + "_temporary_grayscale.png"
    temporary_contrast = images_uid_prefix + "_temporary_contrast.png"
    temporary_noise = images_uid_prefix + "_temporary_noise.png"
    temporary_detect_lines = images_uid_prefix + "_temporary_detect_lines.png"
    '''

    originalImage = Image.open('./images/' + image_to_process_filename)

    originalImage = resizeImage.resizeImg(originalImage, 2000, 1900)

    originalImage = toGrayscale.ToGrayscale(originalImage)

    if apply_dilation:
        originalImage = dilation.dilation(originalImage)
        originalImage = dilation.erosion(originalImage)

    if apply_noise_reduction:
        absoluteImage = noiseRemove.remove_noise(originalImage)
    else:
        absoluteImage = contrastAdjustor.AdjustContrast(originalImage, float(contrast_factor))
        absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)

    utilities.ImageToFile(absoluteImage, './images/' + temporary_black_white_image)
    print("Saved black-white image ", temporary_black_white_image)

    lines, linesCoord = detectLines.DetectLines(absoluteImage, float(segmentation_factor))

    toBoxes.prepareDebug(temporary_black_white_image)  # remove this if you don't want an image with the rectangles
    toBoxes.GetPixels(absoluteImage)
    coordinates = toBoxes.fullFlood(linesCoord, separation_factor)

    with open('./images/' + temporary_black_white_image, 'rb') as file:
        processed_image_payload = (base64.b64encode(file.read())).decode('utf-8')

    # cleanup
    if os.path.exists('./images/' + temporary_black_white_image):
        os.remove('./images/' + temporary_black_white_image)
    if os.path.exists("output_image.jpg"):
        os.remove("output_image.jpg")
    os.remove('./images/' + image_to_process_filename)

    return_data = {
        'names': image_filenames,
        'payloads': images_encoded_content,
        'pName': image_to_process_filename,
        'pPayload': processed_image_payload,
        'coords': coordinates
    }

    if os.path.exists('./images/' + temporary_black_white_image):
        os.remove('./images/' + temporary_black_white_image)

    # return json.dumps(return_data)
    return jsonify(json.dumps(return_data)), 200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
    }


@app.route('/convertPdf', methods=['POST', 'OPTIONS'])
def convert_pdf():
    if request.method == 'OPTIONS':
        return ''

    pdf_file_name = request.json['name']
    pdf_encoded_content = request.json['payload']

    print('Received pdf {}\n'.format(pdf_file_name))

    in_memory_pdf_file = base64.b64decode(pdf_encoded_content)
    open(pdf_file_name, 'wb').write(in_memory_pdf_file)

    images_uid_prefix = str(uuid.uuid4())
    nr_pages = convertPDF2img.convertToJPG(pdf_file_name, images_uid_prefix)

    image_index = 0
    image_filenames = []
    images_encoded_content = []
    files = [f for f in os.listdir('./images') if f.startswith(images_uid_prefix + "_")]
    for i in range(1, nr_pages + 1):
        file = './images/' + images_uid_prefix + '_' + str(i) + '.jpg'
        print(file)
        image_index = image_index + 1
        image_filenames.append(file)
        images_encoded_content.append((base64.b64encode(open(file, 'rb').read())).decode('utf-8'))
        # delete temp img
        os.remove(file)

    # delete pdf
    os.remove(pdf_file_name)

    images_b64_frecv = {}
    for b64 in images_encoded_content:
        md5 = hashlib.md5()
        md5.update(b64.encode())
        b64_hash = md5.hexdigest()
        if b64_hash in images_b64_frecv:
            images_b64_frecv[b64_hash] += 1
        else:
            images_b64_frecv[b64_hash] = 1

    print(images_b64_frecv)

    return_data = {
        'names': image_filenames,
        'payloads': images_encoded_content
    }

    return jsonify(json.dumps(return_data)), 200, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
    }


if __name__ == '__main__':
    sys.setrecursionlimit(2000000)
    app.run(host='0.0.0.0', debug=True, ssl_context=('/home/dorian/AI/server.crt', '/home/dorian/AI/server.key'))
