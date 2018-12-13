import sys
from sys import argv
import cv2
from PIL import Image

width = 0
height = 0
maxW = 0
minW = sys.maxsize
maxH = 0
minH = sys.maxsize

result = list()


def debug(original_image):
    img = cv2.imread(original_image)
    for x in result:
        cv2.rectangle(img, (x[0], x[1]), (x[2], x[3]), (255, 0, 0), 2)
    cv2.imwrite("output_boxes.png", img)


def resetHW():
    global maxW
    global maxH
    global minH
    global minW
    maxW = 0
    minW = sys.maxsize
    maxH = 0
    minH = sys.maxsize


def inMatrix(x, y):
    global width
    global height
    if y < 0 or x < 0 or y > width or x > height:
        return False
    return True


def flood(x, y):
    global pixels
    global maxW
    global maxH
    global minH
    global minW
    if not inMatrix(x, y):
        return
    if pixels[x][y] == 1:
        pixels[x][y] = 2
        if y > maxW:
            maxW = y
        if x > maxH:
            maxH = x
        if y < minW:
            minW = y
        if x < minH:
            minH = x
        flood(x + 1, y)
        flood(x + 1, y + 1)
        flood(x + 1, y - 1)
        flood(x - 1, y)
        flood(x - 1, y + 1)
        flood(x - 1, y - 1)
        flood(x, y - 1)
        flood(x, y + 1)


def GetPixels(inp):
    global width
    global height
    global pixels

    # inp = Image.open(input_path)
    imgPixels = inp.load()
    width, height = inp.size
    pixels = [[0] * width for i in range(height)]

    for i in range(width):
        for j in range(height):
            if imgPixels[i, j][0] == 0:
                pixels[j][i] = 1


def isCompletlyIn(x, y):
    return x[0] < y[0] and x[1] < y[1] and x[2] > y[2] and x[3] > y[3]


def removeRedundant():
    toRemove = list()
    for i in result:
        for j in result:
            if isCompletlyIn(i, j):
                toRemove.append(j)

    for i in toRemove:
        result.remove(i)


def write(file):
    file.write(str(result))


def fullFlood(lines):
    # file = open(output_path, "w+")
    for line in lines:
        for i in range(width):
            for j in range(line[0], line[1]):
                flood(j, i)
                if minH < sys.maxsize:
                    result.append((minW, minH, maxW, maxH))
                    resetHW()
    removeRedundant()
    # write(file)  # remove if you dont want a file
    return result


if __name__ == '__main__':
    if len(argv) != 4:
        print("Usage: [].py inputFile inputLines outputFile")
        exit(0)

    sys.setrecursionlimit(sys.maxsize)  # what do you mean CPU? and RAM?! pfff

    input_path = argv[1]
    lines_path = argv[2]
    output_path = argv[3]

    file = open(lines_path)
    lines = file.readlines()
    coordLines = list()
    for line in range(0, len(lines), 2):
        coordLines.append((int(lines[line]), int(lines[line + 1])))

    #
    GetPixels(Image.open(input_path))
    output = fullFlood(coordLines)
    print(len(output), "boxes:", output)
    #
