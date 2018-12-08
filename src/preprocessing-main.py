import os
from sys import argv

import toGrayscale
import contrastAdjustor
import toBlackWhite

if __name__ == '__main__':
    if (len(argv) < 3 or len(argv) > 4):
        print("Usage: toBlakcWhite.py inputFile outputFile [contrastFactor]")
        exit(0)

    input_path = argv[1]
    output_path = argv[2]
    if (len(argv) == 2):
        contrastFactor = argv[3]
    else:
        contrastFactor = 1
    tempGrayscale = "tempG.jpg"
    tempContrast = "tempC.jpg"

    toGrayscale.ToGrayscale(input_path, tempGrayscale)
    contrastAdjustor.AdjustContrast(tempGrayscale, tempContrast, contrastFactor)
    toBlackWhite.ToBlackAndWhite(tempContrast, output_path)

    # delete temp files
    if os.path.exists(tempGrayscale):
        os.remove(tempGrayscale)
        if os.path.exists(tempContrast):
            os.remove(tempContrast)

