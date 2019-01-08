import random
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


def getW(x):
    return x[0]


def writeDebugImg():
    global debugImg
    cv2.imwrite("output_boxes.png", debugImg)


def addToDebug(rectList):
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for x in rectList:
        cv2.rectangle(debugImg, (x[0], x[1]), (x[2], x[3]), color, 2)


def prepareDebug(original_image):
    global debugImg
    debugImg = cv2.imread(original_image)


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
    if y < 0 or x < 0 or y >= width or x >= height:
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


def removeRedundant(rectangles):
    toRemove = list()
    for i in rectangles:
        for j in rectangles:
            if isCompletlyIn(i, j):
                toRemove.append(j)

    for i in toRemove:
        if i in rectangles:
            rectangles.remove(i)

    return rectangles


def connectClose(rectangles, lineHeight):
    cont = False
    for i in rectangles:
        for j in rectangles:
            if i == j:
                continue
            if i[1] > j[3] - lineHeight / 2 and i[3] > j[3] - lineHeight / 2 and i[0] < (j[0] + j[2]) / 2 < i[2] \
                    and max(i[3], j[3]) - min(i[1], j[1]) < lineHeight * 1.5:
                # toRemove.append(i)
                # toRemove.append(j)
                rectangles.remove(i)
                rectangles.remove(j)
                cont = True
                rectangles.append((min(i[0], j[0]), min(i[1], j[1]), max(i[2], j[2]), max(i[3], j[3])))
                break
        if cont:
            cont = False
            continue


def connect_very_close(rectangles, charDistance):
    error_margin = charDistance
    cont = False
    for i in rectangles:
        for j in rectangles:
            if i == j:
                continue
            if abs(i[2] - j[0]) <= error_margin or (  # W
                    abs(i[3] - j[1]) <= error_margin and j[0] + j[2] - i[0] + i[2] < 5):  # H
                rectangles.remove(i)
                rectangles.remove(j)
                cont = True
                rectangles.append((min(i[0], j[0]), min(i[1], j[1]), max(i[2], j[2]), max(i[3], j[3])))
                break
        if cont:
            cont = False
            continue


def write(file):
    file.write(str(result))


def calc_area(points):
    l1 = points[2] - points[0]
    l2 = points[3] - points[1]
    return l1 * l2


def fullFlood(lines, charDistance = 3):
    # file = open(output_path, "w+")
    nextBoxes = list()
    for line, nextLine in zip(lines, lines[1:] + [(0, 0)]):
        lineBoxes = list()
        lineBoxes.extend(nextBoxes)
        nextBoxes = list()
        for i in range(width):
            for j in range(line[0], line[1]):
                flood(j, i)
                if minH < sys.maxsize:
                    if calc_area((minW, minH, maxW, maxH)) >= height * width * 0.0000074:
                        if line[1] - minH > maxH - nextLine[0] or nextLine == (0, 0):
                            lineBoxes.append((minW, minH, maxW, maxH))
                        else:
                            nextBoxes.append((minW, minH, maxW, maxH))
                    resetHW()
        lineBoxes = list(set(lineBoxes))
        connectClose(lineBoxes, line[1] - line[0])
        lineBoxes.sort(key=getW)
        connect_very_close(lineBoxes, charDistance)
        removeRedundant(lineBoxes)
        lineBoxes.sort(key=getW)
        addToDebug(lineBoxes)
        print(len(lineBoxes))
        result.extend(lineBoxes)

    # write(file)  # remove if you don`t want a file
    return result


if __name__ == '__main__':
    if len(argv) != 4:
        print("Usage: [].py inputFile inputLines outputFile")
        exit(0)

    sys.setrecursionlimit(2000000)  # what do you mean CPU? and RAM?! pfff

    input_path = argv[1]
    lines_path = argv[2]
    output_path = argv[3]

    file = open(lines_path)
    lines = file.readlines()
    coordLines = list()
    for line in range(0, len(lines), 2):
        coordLines.append((int(lines[line]), int(lines[line + 1])))

    #
    prepareDebug(input_path)
    GetPixels(Image.open(input_path))
    output = fullFlood(coordLines)
    writeDebugImg()
    print(len(output), "boxes:", output)
    #
