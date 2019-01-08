import os
from sys import argv
import time

import toGrayscale
import contrastAdjustor
import toBlackWhite
import noiseRemove
import detectLines
import resizeImage
import toBoxes
import dilation
import sys
from utilities import FileToImage, ImageToFile

if __name__ == '__main__':
    if (len(argv) < 2 or len(argv) > 4):
        print("Usage: toBlakcWhite.py inputFile [contrastFactor] [segmentationFactor]")
        exit(0)

    sys.setrecursionlimit(2000000)

    input_path = argv[1]
    if (len(argv) == 3):
        contrastFactor = float(argv[2])
    else:
        contrastFactor = 1.5
        if len(argv) == 4:
            segmentationFactor = float(argv[3])
        else:
            segmentationFactor = 0.45

    id = int(round(time.time() * 1000))
    tempGrayscale = str(id) + "_tempG.jpg"
    tempContrast = str(id) + "_tempC.jpg"
    tempNoise = str(id) + "_tempN.jpg"
    tempBlackWhite = str(id) + "_tempBW.jpg"
    tempDetectLine = str(id) + "_tempDetectLine.jpg"
    tempDilation = str(id) + "_tempDilation.jpg"


    originalImage = FileToImage(input_path)
    startTime = time.time()
    originalImage = resizeImage.resizeImg(originalImage, 2000, 1900)
    resizeTime = time.time()
    print("Time to resize ", resizeTime - startTime, " seconds")

    originalImage = toGrayscale.ToGrayscale(originalImage)
    grayscaleTime = time.time()
    print("Time to grayscale ", grayscaleTime - resizeTime, " seconds")

    #originalImage = dilation.dilation(originalImage)
    #originalImage = dilation.erosion(originalImage)
    dilationTime = time.time()
    print("Time to dilation and erosion ", dilationTime - grayscaleTime, " seconds")

    #absoluteImage = contrastAdjustor.AdjustContrast(originalImage, contrastFactor)
    #absoluteImage = toBlackWhite.ToBlackAndWhite(absoluteImage)
    absoluteImage = noiseRemove.remove_noise(originalImage)
    noiseTime = time.time()
    print("Time to remove noise ", noiseTime - dilationTime, " seconds")
    ImageToFile(absoluteImage, tempBlackWhite)

    afterSaveTime = time.time()
    lines, linesCoord = detectLines.DetectLines(absoluteImage, segmentationFactor)
    linesTime = time.time()
    print("Time to detect lines ", linesTime - afterSaveTime, " seconds")
    ImageToFile(lines, tempDetectLine)

    toBoxes.prepareDebug(tempBlackWhite) # remove this if you don't want an image with the rectangles
    toBoxes.GetPixels(absoluteImage)
    output = toBoxes.fullFlood(linesCoord, 3)
    boxesTime = time.time()
    print("Time to get boxes ", boxesTime - linesTime, " seconds")
    # print(len(output), "boxes:", output)
    f = open("box-p10-n.txt","w+")
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

    
    toBoxes.writeDebugImg() # remove this if you don't want an image with the rectangles

    # delete temp files
    if os.path.exists(tempGrayscale):
        os.remove(tempGrayscale)
        if os.path.exists(tempNoise):
            os.remove(tempNoise)
            if os.path.exists(tempContrast):
                os.remove(tempContrast)

    finalTime = time.time()
    print('Execution time with debuging is ', finalTime - startTime, ' seconds')
