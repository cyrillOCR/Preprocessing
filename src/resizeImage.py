from PIL import Image
import sys
def resizeImg(input_image_path, output_image__path, maxSize, properSize):
    input_image_file = Image.open(input_image_path)
    width, height = input_image_file.size
    percentage = (int(properSize)*100)/int(maxSize)
    percentage = int(percentage)/100
    if width >= int(maxSize):
        percentage = (int(properSize)) / int(width)
        hsize = int((float(height))*float(percentage))
        input_image_file.resize((int(properSize),hsize),Image.ANTIALIAS).save(output_image__path)
    if height >= int(maxSize):
        percentage = (int(properSize))/ int(height)
        wsize = int((float(width)) * float(percentage))
        input_image_file.resize((wsize, int(properSize)), Image.ANTIALIAS).save(output_image__path)


if __name__== '__main__':
    if len(sys.argv) > 5 or len(sys.argv) < 4:
        print("Invalid number of arguments. Usage: resizeImage.py input-image-path output-image-path maxSize properSize")
        exit(-1)
    file_path = sys.argv[1]
    file_path_save = sys.argv[2]
    maxSize = sys.argv[3]
    properSize = sys.argv[4]
    resizeImg(file_path, file_path_save, maxSize, properSize)




