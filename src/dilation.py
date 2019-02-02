from PIL import Image
from sys import argv

"""Only for debugging purposes
"""
def DilationFile(inputPath, outputPath):
    inp = Image.open(input_path)
    out = dilation(inp)
    out.save(outputPath)


"""Determinates the min/max value of neighboring pixels
    :note: find neighborhood value using square mask
    :param width: width of the image
    :param height: height of the image
    :param pixels: a numpy matrix with the grayscale values for each pixel of the image,
        has the type of the structure obtained from Image.open().load()
    :param i: i coordinate of the pixel from the image(from width)
    :param j: j coordinate of the pixel from the image(from height)
    :param type: 1 for maximum value(dilation) and type = 0 for minimum value(erosion)
"""
def NeightborhoodValue(width, height, pixels, i, j, type):
    neightborhoodValues = []
    if i > 0:
        neightborhoodValues += [pixels[i - 1, j][0]]
        if j > 0:
            neightborhoodValues += [pixels[i - 1, j - 1][0]]
        if j < height:
            neightborhoodValues += [pixels[i - 1, j + 1][0]]
    if i < width:
        neightborhoodValues += [pixels[i + 1, j][0]]
        if j > 0:
            neightborhoodValues += [pixels[i + 1, j - 1][0]]
        if j < height:
            neightborhoodValues += [pixels[i + 1, j + 1][0]]
    if j > 0:
        neightborhoodValues += [pixels[i, j - 1][0]]
    if j < height:
        neightborhoodValues += [pixels[i, j + 1][0]]
    if type == 1:
        return min(neightborhoodValues)
    else:
        return max(neightborhoodValues)


"""Apply expansion on the image
    :note: input image should be greyscale
    :param image: the image object returned from Image.open()
    :returns the processed image object(with the same type of Image.open())
"""
def dilation(image):
    out = Image.new(image.mode, image.size)

    originalPixels = image.load()
    newPixels = out.load()
    width, height = image.size

    for i in range(width):
        for j in range(height):
            newValue = NeightborhoodValue(width - 1, height - 1, originalPixels, i, j, 1)
            newPixels[i, j] = (newValue, newValue, newValue)

    return out


"""Apply erosion on the image
    :note: input image should be greyscale
    :param image: the image object returned from Image.open()
    :returns the processed image object(with the same type of Image.open())
"""
def erosion(image):
    out = Image.new(image.mode, image.size)

    originalPixels = image.load()
    newPixels = out.load()
    width, height = image.size

    for i in range(width):
        for j in range(height):
            newValue = NeightborhoodValue(width - 1, height - 1, originalPixels, i, j, 0)
            newPixels[i, j] = (newValue, newValue, newValue)

    return out


if __name__ == '__main__':
    if (len(argv) != 3):
        print("Usage: dilation.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    DilationFile(input_path, output_path)
