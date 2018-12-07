from pprint import pprint
from PIL import Image
from sys import argv



def ToBlackAndWhite(input_path,output_path):
    inp = Image.open(input_path)
    out = Image.new( inp.mode, inp.size)

    originalPixels = inp.load()
    newPixels = out.load()
    width, height = inp.size

    for i in range(width):
        for j in range(height):
            if(originalPixels[i,j][0]<127):
                newPixels[i,j] = (0,0,0)
            else:
                newPixels[i,j] = (255,255,255)
    out.show()
    out.save(output_path)

if __name__=='__main__':
    if(len(argv)!=3):
        print("Usage: toBlakcWhite.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    ToBlackAndWhite(input_path,output_path)