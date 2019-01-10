import base64
import os
import time
import sys
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
import json
from src import contrastAdjustor, noiseRemove, detectLines, toGrayscale, toBlackWhite, toBoxes, utilities, resizeImage, dilation
from src.utilities import ImageToFile, FileToImage

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello world boss"


@app.route('/addImage', methods=['GET'])
def get():
    return "Post only"


@app.route('/addImage', methods=['POST'])
def addImage():
    sys.setrecursionlimit(2000000)
    name = request.json['name']
    payload = request.json['payload']
    contrastFactor = request.json['contrastFactor']
    applyDilation = request.json['applyDilation']
    applyNoiseReduction = request.json['applyNoiseReduction']
    segmentationFactor = request.json['segmentationFactor']
    separationFactor = request.json['separationFactor']

    inputPath = "src/images/image.png"
    outputPath = "src/images/outimage.png"

    if os.path.exists(outputPath):
        os.remove(outputPath)

    if os.path.exists(inputPath):
        os.remove(inputPath)

    image = Image.open(BytesIO(base64.b64decode(payload)))

    # aici se face resize la imagine
    # TREBUIE SA PRIMEASCA image si sa returneze tot o imagine in variabila image

    image.save(inputPath)

    id = int(round(time.time() * 1000))
    tempGrayscale = str(id) + "_tempG.png"
    tempContrast = str(id) + "_tempC.png"
    tempNoise = str(id) + "_tempN.png"
    tempBlackWhite = str(id) + "_tempBW.png"

    originalImage = FileToImage(inputPath)
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
    print("Saved black-white image ", tempBlackWhite)

    lines, linesCoord = detectLines.DetectLines(absoluteImage, float(segmentationFactor))

    toBoxes.prepareDebug(tempBlackWhite)  # remove this if you don't want an image with the rectangles
    toBoxes.GetPixels(absoluteImage)
    output = toBoxes.fullFlood(linesCoord, separationFactor)

    if os.path.exists(tempGrayscale):
        os.remove(tempGrayscale)
        if os.path.exists(tempNoise):
            os.remove(tempNoise)
            if os.path.exists(tempContrast):
                os.remove(tempContrast)

    newPayload = base64.b64encode(open(tempBlackWhite, "rb").read())
    # newPayload = base64.b16encode(absoluteImage)

    data = {
        "name": name,
        "payload": str(newPayload),
        "coords": output
    }
    return json.dumps(data)


if __name__ == '__main__':
    sys.setrecursionlimit(2000000)
    app.run(host= '0.0.0.0')
