from pdf2image import convert_from_path
import tempfile
from sys import argv
import PyPDF2
import os


def getNumberOfPages(path):
    pdfFileObj = open(path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    nr = pdfReader.numPages
    pdfFileObj.close()

    return nr


def savePages(input_file, path, first_p, last_p, page_index, prefix_id):
    pages = convert_from_path(input_file, dpi=100, output_folder=path,
                              thread_count=4,
                              fmt="JPEG", last_page=last_p, first_page=first_p)
    for page in pages:
        page_index += 1
        page.save("images/" + str(prefix_id) + "_" + str(page_index) + ".jpg")
    return page_index


def convertToJPG(input_file, prefix_id):
    with tempfile.TemporaryDirectory() as path:
        if os.path.exists("./images") == False:
            os.mkdir('./images')

        total_pages = getNumberOfPages(input_file)
        if total_pages <= 5:
            savePages(input_file, path, 1, total_pages, 1, prefix_id)
            return None

        nr_pages = 5
        last_page_index = 0
        while total_pages >= 5:
            try:
                last_page_index = savePages(input_file, path, last_page_index + 1, last_page_index + nr_pages,
                                            last_page_index, prefix_id)
                total_pages -= nr_pages
            except Exception as err:
                print(err)

        if total_pages > 0:
            savePages(input_file, path, last_page_index + 1, last_page_index + nr_pages, last_page_index, prefix_id)
    return total_pages

def deletePages(prefix_id, total_pages):
    i = 1
    while i <= total_pages:
        file = "./images/" + repr(prefix_id) + "_" + repr(i) + ".jpg"
        if os.path.exists(file):
            os.remove(file)
        else:
            break
        i += 1


if __name__ == '__main__':
    if (len(argv) != 3):
        print("Usage: convertPDF2img.py inputFile prefix_id")
        exit(0)

    input_path = argv[1]
    prefix_id = int(argv[2])
    convertToJPG(input_path, prefix_id)
