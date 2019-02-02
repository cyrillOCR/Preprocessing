from pprint import pprint
from PIL import Image
from sys import argv

"""Converts a RGB image file to a Grayscale image file, using ToGrayscale
    :param inputPath: the path to a the input file that needs to be processed
    :param outputPath: the path where the result of the operation goes
"""
def ToGrayscaleFile(inputPath,outputPath):
    inp = Image.open(input_path)
    out = ToGrayscale(inp)
    out.save(outputPath)


"""Converts all the pixels from RGB to Grayscale using the formula 0.21 R + 0.72 G + 0.07 B
    :param image: a PIL.Image object that we want to convert from RGB to Grayscale
"""
def ToGrayscale(image):
    out = Image.new( image.mode, image.size)

    originalPixels = image.load()
    newPixels = out.load()
    width, height = image.size

    for i in range(width):
        for j in range(height):
            # 0.21 R + 0.72 G + 0.07 B.
            grayscaleValue = int(0.21*originalPixels[i,j][0]+0.72*originalPixels[i,j][1]+0.07*originalPixels[i,j][2])
            newPixels[i,j] = (grayscaleValue,grayscaleValue,grayscaleValue)
    # decomment this to show result file
    #out.show()
    return out

if __name__=='__main__':
    if(len(argv)!=3):
        print("Usage: toGrayscale.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    ToGrayscaleFile(input_path,output_path)