from pprint import pprint
from PIL import Image
from math import pow
from sys import argv


def AdjustContrast(input_path,output_path,contrastFactor):
    inp = Image.open(input_path)
    out = Image.new( inp.mode, inp.size)

    originalPixels = inp.load()
    newPixels = out.load()
    width, height = inp.size

    for i in range(width):
        for j in range(height):
            grayscaleValue = int(originalPixels[i,j])
            contrastValue = int(pow(float(grayscaleValue)*2.0/255.0,contrastFactor)/2.0*255.0)
            newPixels[i,j] = (contrastValue)

    out.show()
    out.save(output_path)

if __name__=='__main__':
    if(len(argv)!=4):
        print("Usage: contrastAdjustor.py inputFile outputFile contrastFactor")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    contrastFactor = float(argv[3])
    AdjustContrast(input_path,output_path,contrastFactor)