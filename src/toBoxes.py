import random
import sys
from sys import argv
import cv2
from PIL import Image

"""
Width and Height of the input image
"""
width = 0
height = 0


"""
Every box is saved as two points, the upper left and the lower right.
Upper left = (minW,maxH)
Lower right = (maxW,minH)

  0     1      2    3
(minW, minH, maxW, maxH)

These are updated every time it finds a box and reset to these values after the box is saved
"""
maxW = 0
minW = sys.maxsize
maxH = 0
minH = sys.maxsize

result = list()


"""
Q: Why didn't you use a class for points? Why an array?
A: Back when I wrote this I didn't think it had to be mentained so I just wrote it to work and no to look pretty
"""
def getW(x):
    return x[0]


"""
Writes the debug image
	:param output_name: name of the debug image to write on disk
"""
def writeDebugImg(output_name):
    global debugImg
    cv2.imwrite(output_name, debugImg)


"""
Adds a list of rectangles to the debug image, prepareDebug MUST be called before using this, failing to do so will result in an error
	:param rectList: list to add to the debug image
"""
def addToDebug(rectList):
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for x in rectList:
        cv2.rectangle(debugImg, (x[0], x[1]), (x[2], x[3]), color, 2)


"""
Initialization for debugging. This is the first debug function to call for debugging. After this call addToDebug with lists to add and writeDebugImage to write the image to the disk.
The debug image is the original input with the boxes drawn for each character in the text with a different (random) color for each line
	:param original_image: the original image to draw the boxes over
"""
def prepareDebug(original_image):
    global debugImg
    debugImg = cv2.imread(original_image)


"""
Resets all the global values for storing the current point
"""
def resetHW():
    global maxW
    global maxH
    global minH
    global minW
    maxW = 0
    minW = sys.maxsize
    maxH = 0
    minH = sys.maxsize


"""
Resets all the global values including the result list, should call this function after each run
"""
def reset():
    global result
    resetHW()
    result = list()


"""
Checks if a point (x,y) has valid coordinates for the current image
	:param x: x coord
	:param y: y coord
	:returns true if the point is valid
"""


def inMatrix(x, y):
    global width
    global height
    if y < 0 or x < 0 or y >= width or x >= height:
        return False
    return True


"""
Starts a flood on the pixel matrix starting from the point (x,y). GetPixels MUST be called prior to this.
First it checks if the input is valid (inMatrix) then checks if this point is not visited and a black pixel (pixels[x][y] == 1).
If the point is not visited and part of a character (black) it updated the global variables for the current box.
Then it will recursively call itself for all 8 adjacent pixels.
The flood will stop when there is no black point connected to any of the proccesed points.
	:param x: x coord
	:param y: y coord
"""
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


"""
Loads an image in memory as a pixel matrix ( pixels[x][y] = 1 if the point (x,y) is black). Also sets the global width and height
	:param inp: image to load, this should be what you get from Image.open(input_path)
"""
def GetPixels(inp):
    global width
    global height
    global pixels

    reset()
    # inp = Image.open(input_path)
    imgPixels = inp.load()
    width, height = inp.size
    pixels = [[0] * width for i in range(height)]

    for i in range(width):
        for j in range(height):
            if imgPixels[i, j][0] == 0:
                pixels[j][i] = 1


"""
Checks if a rectangle is completly in another rectangle (the smaller one will be removed later)
	:returns true if y is in x
"""
def isCompletlyIn(x, y):
    return x[0] < y[0] and x[1] < y[1] and x[2] > y[2] and x[3] > y[3]


"""
Removes rectangles that are completly in another rectangle
	:param rectangles: list of rectangles to remove from
	:returns the list without them
"""
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


"""
Connects rectangles in a list, it will connect two rectangles if:
1. they are not further than half the line height from each other (up or down)
2. the center (in width) is inside the other one (ex: (1,5) and (2,8). The "center" of (1,5) is 3 and it is inside (2,8))
3. the two combined are not taller than lineHeight*1.5
	:param rectangles: list of rectangles to try to connect
	:param lineHeight: the height of the current line (all the rectangles MUST be from the same text line)
"""
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


"""
Connects rectangles in a list that have at least one pixel from each at a distance smaller than charDistance
	:param rectangles: list of rectangles to try to connect
	:param charDistance: max distance between points from each rectangle
"""
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


"""
Calculates the area of a rectangle
	:param points:
	:returns the area
"""
def calc_area(points):
    l1 = points[2] - points[0]
    l2 = points[3] - points[1]
    return l1 * l2


"""
This is the "main" function.
For each line it calls the flood for each point in the line. If the flood changed the global variables it means it found a rectangle. If the rectangle area is smaller than [height * width * 0.0000074] it is not added.
If the rectangle is mostly out of the line then it is added to a list for the next line.
After we have a list of rectangles for a line we remove duplicates and:
1. connectClose
2. sort it (so that the boxes are from left to right, up to bottom)
3. connect_very_close
4. removeRedundant
5. sort it again
6. addToDebug (if you want a debug image, else remove this line)
7. add to the final result list that will contain all rectangles

We sort twice because connect_very_close and removeRedundant work faster on a sorted list but may destroy the order

	:param lines: list of all text lines
	:param charDistance: passed to connect_very_close
	:returns a list of all rectangles from the image
"""
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
        addToDebug(lineBoxes) #!!! Remove if you don't want a debug image
        #print(len(lineBoxes))
        result.extend(lineBoxes)

    # write(file)  # remove if you don`t want a file
    return result


"""
About "sys.setrecursionlimit(2000000)":
In short, this uses a recursive function many times, python doesn't like that, the stack frames in python are too big, python is really not made for this.
This instruction sets the max recursion limit very high so it won't rise any problems. A permanent solution would be to rewrite the "flood" function iteratively so there would be no recursion
"""
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
