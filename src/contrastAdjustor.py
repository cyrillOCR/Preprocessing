from pprint import pprint
from PIL import Image
from math import pow
from sys import argv

def AdjustContrastFile(inputPath,outputPath,contrastFactor):
    inp = Image.open(inputPath)
    out = AdjustContrast(inp,contrastFactor)
    out.save(outputPath)


def AdjustContrast(image,contrastFactor):
    out = Image.new( image.mode, image.size)

    originalPixels = image.load()
    newPixels = out.load()
    width, height = image.size

    for i in range(width):
        for j in range(height):
            grayscaleValue = int(originalPixels[i,j][0])
            contrastValue = int(pow(float(grayscaleValue)*2.0/255.0,contrastFactor)/2.0*255.0)
            newPixels[i,j] = (contrastValue,contrastValue,contrastValue)
    # decomment this to show result file
    # out.show()
    return out

if __name__=='__main__':
    if(len(argv)!=4):
        print("Usage: contrastAdjustor.py inputFile outputFile contrastFactor")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    contrastFactor = float(argv[3])
    AdjustContrastFile(input_path,output_path,contrastFactor)