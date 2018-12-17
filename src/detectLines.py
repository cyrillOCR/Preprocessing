from PIL import Image
from sys import argv


def getAveragePixelsPerLine(pixelRowSum):
    return sum(pixelRowSum) / max(len(pixelRowSum), 1)


def getAverageLineHeight(pixelRowMarked):
    average = 0
    nrLines = 0
    height = 0
    for i in range(len(pixelRowMarked)):
        if pixelRowMarked[i] == 1:
            height += 1
        else:
            if height > 0:
                average += height
                height = 0
                nrLines += 1
    if height > 0:
        nrLines += 1
        average += height
    return average / nrLines


def getMinPixelsAllowed(average, segmentationFactor):
    return segmentationFactor * average


def getMedianDistanceBetweenLines(pixelRowMarked):
    spaceHeight = list()
    height = 0
    for i in range(len(pixelRowMarked)):
        if pixelRowMarked[i] == 1:
            if height != 0:
                spaceHeight.append(height)
                height = 0
        else:
            height += 1
    spaceHeight.sort()
    return spaceHeight[int(len(spaceHeight) / 2)]


def combineSmallLines(pixelRowMarked):
    averageHeight = getAverageLineHeight(pixelRowMarked)
    spaceMedianHeight = getMedianDistanceBetweenLines(pixelRowMarked)
    height = 0
    l = len(pixelRowMarked)
    i = 0
    while i < l:
        if pixelRowMarked[i] == 1:
            height += 1
        else:
            # if is a small line
            if height < averageHeight * 0.5 and height != 0:
                # print("Linia mica: " + str(i))
                # if the space above is much bellow the median concatenate the tall line with the line above
                # else if the space bellow is much bellow the median concatenate the tall line with the line bellow
                j = i - height - 1
                while j > 0 and pixelRowMarked[j] == 0:
                    j -= 1
                # print("Inaltime spatiu deasupra: " + str(i - j))
                if j > 0 and (i - j <= spaceMedianHeight * 0.5 or i - j <= 3):
                    # concatenate with the line above, by turn white pixel into black
                    while j < i - height:
                        pixelRowMarked[j] = 1
                        j += 1
                else:
                    j = i
                    while j < len(pixelRowMarked) and pixelRowMarked[j] == 0:
                        j += 1

                    if j < len(pixelRowMarked) and (j - i <= spaceMedianHeight * 0.5 or j - i <= 3):
                        aux = j
                        while j >= i:
                            pixelRowMarked[j] = 1
                            j -= 1
                        height = height + aux - i + 1
                        i = aux
                        i += 1
                        continue
            height = 0
        i += 1
    return pixelRowMarked


def deleteSmallLines(pixelRowMarked):
    averageHeight = getAverageLineHeight(pixelRowMarked)
    height = 0
    for i in range(len(pixelRowMarked)):
        if pixelRowMarked[i] == 1:
            height += 1
        else:
            if height > 0 and height < 0.4 * averageHeight:
                j = i - height
                while j < i:
                    pixelRowMarked[j] = 0
                    j += 1
            height = 0
    return pixelRowMarked


def DetectLinesFile(inputPath, outputPath, segmentationFactor):
    inp = Image.open(inputPath)
    out, coords = DetectLines(inp, segmentationFactor)
    out.save(outputPath)
    print(coords)
    f = open("lines.txt","w+")
    for c in coords:
        f.write(str(c[0]))
        f.write("\n")
        f.write(str(c[1]))
        f.write("\n")


# return a list of tuples for each line detected: (upper bound of line, lower bound of line)
def DetectLines(inp, segmentationFactor):
    out = Image.new(inp.mode, inp.size)

    originalPixels = inp.load()
    newPixels = out.load()
    width, height = inp.size

    pixelRowSum = list()
    pixelRowMarked = list()

    for i in range(height):
        sum = 0
        for j in range(width):
            if originalPixels[j, i][0] < 128:
                sum += 1
        pixelRowSum.append(sum)

    average = getAveragePixelsPerLine(pixelRowSum)
    for i in range(len(pixelRowSum)):
        if (pixelRowSum[i] > getMinPixelsAllowed(average, segmentationFactor)):
            pixelRowMarked.append(1)
        else:
            pixelRowMarked.append(0)

    pixelRowMarked = combineSmallLines(pixelRowMarked)
    pixelRowMarked = deleteSmallLines(pixelRowMarked)

    for i in range(width):
        for j in range(height):
            if (pixelRowMarked[j] == 0):
                newPixels[i, j] = (0)
            else:
                newPixels[i, j] = (255)

    coord = list()
    height = 0
    up = 0
    lw = 0
    for i in range(len(pixelRowMarked)):
        if pixelRowMarked[i] == 1:
            if height == 0:
                up = i
            height += 1
        else:
            if height > 0:
                lw = i - 1
                coord.append((up, lw))
            height = 0
    return out, coord


if __name__ == '__main__':
    if (len(argv) != 3):
        print("Usage: detectLines.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    DetectLinesFile(input_path, output_path)
