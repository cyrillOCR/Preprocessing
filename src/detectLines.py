from pprint import pprint
from PIL import Image
from math import pow
from sys import argv


def DetectLines(input_path,output_path):
    inp = Image.open(input_path)
    out = Image.new( inp.mode, inp.size)

    originalPixels = inp.load()
    newPixels = out.load()
    width, height = inp.size

    pixelRowSum = list()
    pixelRowMarked = list()

    for i in range(height):
        sum = 0
        for j in range(width):
            if originalPixels[j,i] < 128:
                sum += 1
        pixelRowSum.append(sum)
    print(pixelRowSum)

    for i in range(len(pixelRowSum)):
        if(pixelRowSum[i] > width/30):
            pixelRowMarked.append(1)
        else:
            pixelRowMarked.append(0)
    print(pixelRowMarked)
    
    for i in range(width):
        for j in range(height):
            if(pixelRowMarked[j] == 0):
                newPixels[i,j] = (0)
            else:
                newPixels[i,j] = (255)
    out.show()
    out.save(output_path)


if __name__=='__main__':
    if(len(argv)!=3):
        print("Usage: detectLines.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    DetectLines(input_path,output_path)