from pprint import pprint
from PIL import Image
from sys import argv

"""Opens a grayscale file, and then users ToBlackAndWhite to convert it to only pure black and pure white
    :param inputPath: the path to a the input file that needs to be processed
    :param outputPath: the path where the result of the operation goes
"""
def ToBlackAndWhiteFile(inputPath,outputPath):
    inp = Image.open(input_path)
    out = ToBlackAndWhite(inp)
    out.save(outputPath)


"""Converts all the pixels from grayscale to pure black and pure white using a PIL.Image object
    :param image: a PIL.Image object that we want to convert
"""
def ToBlackAndWhite(image):
    out = Image.new( image.mode, image.size)

    originalPixels = image.load()
    newPixels = out.load()
    width, height = image.size

    for i in range(width):
        for j in range(height):
            if(originalPixels[i,j][0]<127):
                newPixels[i,j] = (0,0,0)
            else:
                newPixels[i,j] = (255,255,255)
    # decomment this to show result file
    # out.show()
    return out

if __name__=='__main__':
    if(len(argv)!=3):
        print("Usage: toBlakcWhite.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    ToBlackAndWhiteFile(input_path,output_path)