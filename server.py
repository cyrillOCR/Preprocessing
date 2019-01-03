import base64
import os
import time
import sys
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
import json
from src import contrastAdjustor, noiseRemove, detectLines, toGrayscale, toBlackWhite, toBoxes, utilities, resizeImage
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

    # aici se face resize la imagine
    # TREBUIE SA PRIMEASCA image si sa returneze tot o imagine in variabila image

    image.save(inputPath)

    id = int(round(time.time() * 1000))
    tempGrayscale = str(id) + "_tempG.png"
    tempContrast = str(id) + "_tempC.png"
    tempNoise = str(id) + "_tempN.png"
    tempBlackWhite = str(id) + "_tempBW.png"
    tempDetectLine = str(id) + "_tempDetectLine.png"

    originalImage = FileToImage(inputPath)
    originalImage = toGrayscale.ToGrayscale(originalImage)
    #ImageToFile(originalImage, tempGrayscale)

    absoluteImage = contrastAdjustor.AdjustContrast(originalImage, float(contrastFactor))

    # aici se proceseaza noise-ul
    # TREBUIE SA PRIMEASCA absoluteImage si sa returneze imaginea tot in variabila absoluteImage
    if applyNoiseReduction:
        absoluteImage = noiseRemove.remove_noise(absoluteImage)

    absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)
    ImageToFile(absoluteImage, tempBlackWhite)

    lines, linesCoord = detectLines.DetectLines(absoluteImage, float(segmentationFactor))
    #print(linesCoord)
    #ImageToFile(lines, tempDetectLine)

    toBoxes.GetPixels(absoluteImage)
    output = toBoxes.fullFlood(linesCoord)
    print(len(output), "boxes:", output)

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
