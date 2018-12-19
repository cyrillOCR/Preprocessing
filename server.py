import base64
import os
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
import json

from src import contrastAdjustor, noiseRemove, detectLines

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello world"


@app.route('/addImage', methods=['GET'])
def get():
    return "Post only"

@app.route('/addImage', methods=['POST'])
def addImage():
    name = request.json['name']
    payload = request.json['payload']
    contrastFactor = request.json['contrastFactor']
    applyNoiseReduction = request.json['applyNoiseReduction']
    noiseReductionFactor = request.json['noiseReductionFactor']
    segmentationFactor = request.json['segmentationFactor']

    inputPath = "src/images/image.png"
    outputPath = "src/images/outimage.png"

    if os.path.exists(outputPath):
        os.remove(outputPath)

    if os.path.exists(inputPath):
        os.remove(inputPath)

    image = Image.open(BytesIO(base64.b64decode(payload)))
    image.save(inputPath)
    # image.show()

    if contrastFactor:
        contrastAdjustor.AdjustContrastFile(inputPath, outputPath, float(contrastFactor))

    if applyNoiseReduction:
        noiseRemove.remove_noise(outputPath, outputPath, int(noiseReductionFactor))

    # coords = detectLines.DetectLinesFile(inputPath, outputPath, float(segmentationFactor))

    newPayload = base64.b16encode(open(outputPath, "rb").read())

    data = {
        "name": name,
        "payload": str(newPayload),
        "coords": detectLines.DetectLinesFile(inputPath, outputPath, float(segmentationFactor))
    }
    return json.dumps(data)


if __name__ == '__main__':
    app.run()
