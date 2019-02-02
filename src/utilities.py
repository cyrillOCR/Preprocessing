from PIL import Image

"""Opens an image file from a path and converts it to an PIL.Image object
    :inputPath: the path of the image file
"""
def FileToImage(inputPath):
    inp = Image.open(inputPath)
    return inp

"""Takes a PIL.Image object and then saves it to the disk
    :param image: a PIL.Image object
    :outputPath: the path where we want to save the image
"""
def ImageToFile(image, outputPath):
    image = image.convert("RGB")
    image.save(outputPath)
