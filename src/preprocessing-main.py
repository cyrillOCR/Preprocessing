import os
from sys import argv

import toGrayscale
import contrastAdjustor
import toBlackWhite
import noiseRemove
import detectLines
from utilities import FileToImage, ImageToFile

if __name__ == '__main__':
    if (len(argv) < 3 or len(argv) > 4):
        print("Usage: toBlakcWhite.py inputFile outputFile [contrastFactor]")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    if (len(argv) == 2):
        contrastFactor = argv[3]
    else:
        contrastFactor = 1.5
    tempGrayscale = "tempG.jpg"
    tempContrast = "tempC.jpg"
    tempNoise = "tempN.jpg"
    tempBlackWhite = "tempBW.jpg"
    tempDetectLine = "tempDetectLine.jpg"

    originalImage = FileToImage(input_path)
    originalImage = toGrayscale.ToGrayscale(originalImage)
    ImageToFile(originalImage, tempGrayscale)

    absoluteImage = contrastAdjustor.AdjustContrast(originalImage, contrastFactor)
    absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)
    ImageToFile(absoluteImage, tempBlackWhite)

    _, linesCoord = detectLines.DetectLines(absoluteImage)
    print(linesCoord)
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
