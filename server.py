import base64
import os
import time
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
import json
from src import contrastAdjustor, noiseRemove, detectLines, toGrayscale, toBlackWhite, toBoxes, utilities
from src.utilities import ImageToFile, FileToImage

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
    #
    # image = toGrayscale.ToGrayscale(image)
    # # ImageToFile(image, tempGrayscale)
    #
    # if contrastFactor:
    #     contrastAdjustor.AdjustContrast(image, float(contrastFactor))
    #     toBlackWhite.ToBlackAndWhite(image)
    #     # ImageToFile(absImage, tempBlackWhite) /
    #
    # if applyNoiseReduction:
    #     noiseImage = noiseRemove.remove_noise(inputPath, outputPath, int(noiseReductionFactor))
    #
    #
    #
    # # coords = detectLines.DetectLinesFile(inputPath, outputPath, float(segmentationFactor))
    #
    # lines, linesCoord = detectLines.DetectLines(open(outputPath), float(segmentationFactor))
    # print(linesCoord)
    # # ImageToFile(lines, tempDetectLine)
    #
    # toBoxes.GetPixels(open(outputPath))
    # output = toBoxes.fullFlood(linesCoord)
    # print(len(output), "Boxes:", output)
    #

    id = int(round(time.time() * 1000))
    tempGrayscale = str(id) + "_tempG.png"
    tempContrast = str(id) + "_tempC.png"
    tempNoise = str(id) + "_tempN.png"
    tempBlackWhite = str(id) + "_tempBW.png"
    tempDetectLine = str(id) + "_tempDetectLine.png"

    originalImage = FileToImage(inputPath)
    originalImage = toGrayscale.ToGrayscale(originalImage)
    ImageToFile(originalImage, tempGrayscale)

    absoluteImage = contrastAdjustor.AdjustContrast(originalImage, float(contrastFactor))
    absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)
    ImageToFile(absoluteImage, tempBlackWhite)

    lines, linesCoord = detectLines.DetectLines(absoluteImage, float(segmentationFactor))
    print(linesCoord)
    ImageToFile(lines, tempDetectLine)

    toBoxes.GetPixels(absoluteImage)
    output = toBoxes.fullFlood(linesCoord)
    print(len(output), "boxes:", output)
    f = open("i5.txt", "w+")
    for b in output:
        f.write("(")
        f.write(str(b[0]))
        f.write(", ")
        f.write(str(b[1]))
        f.write(", ")
        f.write(str(b[2]))
        f.write(", ")
        f.write(str(b[3]))
        f.write(")\n")
    f.close()

    toBoxes.debug(inputPath)

    if applyNoiseReduction:
        noiseRemove.remove_noise(tempGrayscale, tempNoise, int(noiseReductionFactor))

    if os.path.exists(tempGrayscale):
        os.remove(tempGrayscale)
        if os.path.exists(tempNoise):
            os.remove(tempNoise)
            if os.path.exists(tempContrast):
                os.remove(tempContrast)

    newPayload = base64.b16encode(open(tempBlackWhite, "rb").read())
    # newPayload = base64.b16encode(absoluteImage)

    data = {
        "name": name,
        "payload": str(newPayload),
        "coords": output
    }
    return json.dumps(data)


if __name__ == '__main__':
    app.run()
