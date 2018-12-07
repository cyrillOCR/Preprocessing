import argparse
import csv

import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
# ^ change this if installed on another path


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be parsed")
args = vars(ap.parse_args())

img = cv2.imread(args["image"])

# img = cv2.imread(filename)
h, w, _ = img.shape
text = pytesseract.image_to_boxes(img, lang="rus").encode("utf-8")

file = open("boxes.txt", mode="wb")
file.write(text)
file.close()

boxes = []
coords = []
with open('boxes.txt', 'r', encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=' ')
    for row in reader:
        if len(row) == 6:
            boxes.append(row)

for b in boxes:
    img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (255, 0, 0), 2)
    coords.append((int(b[1]), h - int(b[2]), int(b[3]), h - int(b[4])))

print(coords)

file = open("output.txt", mode="w+")
file.write('\n'.join(str(e) for e in coords))
file.close()

cv2.imwrite("output.png", img)

# cv2.imshow('output', img)

cv2.waitKey(0)
