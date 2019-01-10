from PIL import Image
from sys import argv


def DilationFile(inputPath, outputPath):
    inp = Image.open(input_path)
    out = dilation(inp)
    out.save(outputPath)


# find max neighborhood value using square mask
# type = 1 for dilation and type = 0 for erosion
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


# input image should be greyscale
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

# input image should be greyscale
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