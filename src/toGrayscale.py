from pprint import pprint
from PIL import Image
from sys import argv


def ToGrayscale(input_path,output_path):
    inp = Image.open(input_path)
    out = Image.new( inp.mode, inp.size)

    originalPixels = inp.load()
    newPixels = out.load()
    width, height = inp.size

    for i in range(width):
        for j in range(height):
            # 0.21 R + 0.72 G + 0.07 B.
            grayscaleValue = int(0.21*originalPixels[i,j][0]+0.72*originalPixels[i,j][1]+0.07*originalPixels[i,j][2])
            newPixels[i,j] = (grayscaleValue,grayscaleValue,grayscaleValue)
    out.show()
    out.save(output_path)

if __name__=='__main__':
    if(len(argv)!=3):
        print("Usage: toGrayscale.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    ToGrayscale(input_path,output_path)