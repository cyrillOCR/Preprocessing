import os
from sys import argv
import time

import toGrayscale
import contrastAdjustor
import toBlackWhite
import noiseRemove
import detectLines
import toBoxes
import sys
from utilities import FileToImage, ImageToFile

if __name__ == '__main__':
    if (len(argv) < 2 or len(argv) > 3):
        print("Usage: toBlakcWhite.py inputFile [contrastFactor]")
        exit(0)

    sys.setrecursionlimit(sys.maxsize)

    input_path = argv[1]
    if (len(argv) == 3):
        contrastFactor = argv[2]
    else:
        contrastFactor = 1.5

    id = int(round(time.time() * 1000))
    tempGrayscale = str(id) + "_tempG.jpg"
    tempContrast = str(id) + "_tempC.jpg"
    tempNoise = str(id) + "_tempN.jpg"
    tempBlackWhite = str(id) + "_tempBW.jpg"
    tempDetectLine = str(id) + "_tempDetectLine.jpg"


    originalImage = FileToImage(input_path)
    originalImage = toGrayscale.ToGrayscale(originalImage)
    ImageToFile(originalImage, tempGrayscale)

    absoluteImage = contrastAdjustor.AdjustContrast(originalImage, contrastFactor)
    absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)
    ImageToFile(absoluteImage, tempBlackWhite)

    lines, linesCoord = detectLines.DetectLines(absoluteImage)
    print(linesCoord)
    ImageToFile(lines, tempDetectLine)

    toBoxes.GetPixels(absoluteImage)
    output = toBoxes.fullFlood(linesCoord)
    print(len(output), "boxes:", output)
    f = open("i5.txt","w+")
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

    toBoxes.debug(input_path) # remove this if you don't want an image with the rectangles
    # noiseRemove.remove_noise(tempGrayscale, tempNoise, 65)

    # delete temp files
    if os.path.exists(tempGrayscale):
        os.remove(tempGrayscale)
        if os.path.exists(tempNoise):
            os.remove(tempNoise)
            if os.path.exists(tempContrast):
                os.remove(tempContrast)
                if os.path.exists(tempBlackWhite):
                    os.remove(tempBlackWhite)
