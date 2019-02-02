from PIL import Image
from sys import argv
"""Rescales image according to some desired size
    :param image: a given image
    :param maxSize: a number representing an upper bound for the number of pixels
    :param properSize: a number representing the new, expected maximum number of pixels after refactoring
"""
def resizeImg(image, maxSize, properSize):
    width, height = image.size
    percentage = (int(properSize)*100)/int(maxSize)
    percentage = int(percentage)/100
    if width >= int(maxSize):
        percentage = (int(properSize)) / int(width)
        hsize = int((float(height))*float(percentage))
        image = image.resize((int(properSize),hsize),Image.ANTIALIAS)
    if height >= int(maxSize):
        percentage = (int(properSize))/ int(height)
        wsize = int((float(width)) * float(percentage))
        image = image.resize((wsize, int(properSize)), Image.ANTIALIAS)
    return image



if __name__== '__main__':
    if len(argv)!=4:
        print("Invalid number of arguments. Usage: resizeImage.py image_path maxSize properSize")
        exit(-1)
    image_path = argv[1]
    maxSize = argv[2]
    properSize = argv[3]
    image = Image.open(image_path)
    image = resizeImg(image, maxSize, properSize)
    image.show()









