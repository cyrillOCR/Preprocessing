from pprint import pprint
from PIL import Image
from math import pow
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
        nrLines +=1
        average += height
    return average/nrLines

def getMinPixelsAllowed(average, width):
    return 0.45 * average

def getMedianDistanceBetweenLines(pixelRowMarked):
    spaceHeight = list()
    height = 0
    for i in range(len(pixelRowMarked)):
        if pixelRowMarked[i] == 1:
            if height !=0:
                spaceHeight.append(height)
                height = 0
        else:
            height +=1
    spaceHeight.sort()
    print("Inaltimi spatii:")
    print(spaceHeight)
    return spaceHeight[int(len(spaceHeight)/2)]

def combineSmallLines(pixelRowMarked):
    averageHeight = getAverageLineHeight(pixelRowMarked)
    spaceMedianHeight = getMedianDistanceBetweenLines(pixelRowMarked)
    print("Inaltime medie linie " + str(averageHeight))
    print("Mediana spatiu dintre linii " + str(spaceMedianHeight))
    height = 0
    l = len(pixelRowMarked)
    i = 0
    while i < l:
        if pixelRowMarked[i] == 1:
            height += 1
        else:
            # if is a small line
            if height < averageHeight * 0.5 and height != 0:
                #print("Linia mica: " + str(i))
                # if the space above is much bellow the median concatenate the tall line with the line above
                # else if the space bellow is much bellow the median concatenate the tall line with the line bellow
                j = i - height - 1
                while j > 0 and pixelRowMarked[j] == 0:
                    j -= 1
                #print("Inaltime spatiu deasupra: " + str(i - j))
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

def DetectLines(input_path,output_path):
    inp = Image.open(input_path)
    out = Image.new( inp.mode, inp.size)

    originalPixels = inp.load()
    newPixels = out.load()
    width, height = inp.size

    pixelRowSum = list()
    pixelRowMarked = list()

    for i in range(height):
        sum = 0
        for j in range(width):
            if originalPixels[j,i] < 128:
                sum += 1
        pixelRowSum.append(sum)

    average = getAveragePixelsPerLine(pixelRowSum)
    for i in range(len(pixelRowSum)):
        #if(pixelRowSum[i] > width/30):
        if (pixelRowSum[i] > getMinPixelsAllowed(average, width)):
            pixelRowMarked.append(1)
        else:
            pixelRowMarked.append(0)

    pixelRowMarked = combineSmallLines(pixelRowMarked)
    pixelRowMarked = deleteSmallLines(pixelRowMarked)
    
    for i in range(width):
        for j in range(height):
            if(pixelRowMarked[j] == 0):
                newPixels[i,j] = (0)
            else:
                newPixels[i,j] = (255)
    out.show()
    out.save(output_path)


if __name__=='__main__':
    if(len(argv)!=3):
        print("Usage: detectLines.py inputFile outputFile")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    DetectLines(input_path,output_path)