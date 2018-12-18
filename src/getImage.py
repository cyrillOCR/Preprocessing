import base64
from flask import Flask, json, send_from_directory, url_for, request, jsonify
import os
from PIL import Image
from io import BytesIO

from src import contrastAdjustor, noiseRemove, detectLines

app = Flask(__name__)


@app.route('/multipart/form-data', methods=['PoST'])
def addImage():
    name = request.json['name']
    payload = request.json['payload']
    contrastFactor = request.json['contrastFactor']
    applyNoiseReduction = request.json['applyNoiseReduction']
    noiseReductionFactor = request.json['noiseReductionFactor']
    segmentationFactor = request.json['segmentationFactor']

    image = Image.open(BytesIO(base64.b64decode(payload)))
    modifiedImage = image

    if contrastFactor:
        contrastAdjustor.AdjustContrast(image, modifiedImage, contrastFactor)

    if applyNoiseReduction:
        noiseRemove.remove_noise(image, modifiedImage, noiseReductionFactor)

    coords = detectLines.DetectLines(image, segmentationFactor)

    return jsonify(
        name=name,
        payload=BytesIO(base64.b16encode(modifiedImage)),
        coords=coords
    )


if __name__ == '__main__':
    app.run()
