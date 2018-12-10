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


def savePages(input_file, path, first_p, last_p, page_index):
    pages = convert_from_path(input_file, dpi=100, output_folder=path,
                              thread_count=4,
                              fmt="JPEG", last_page=last_p, first_page=first_p)
    for page in pages:
        page_index += 1
        page.save("output/img" + repr(page_index) + ".jpg")
    return page_index


def convertToJPG(input_file):
    with tempfile.TemporaryDirectory() as path:
        if os.path.exists("./output") == False:
            os.mkdir('./output')
        total_pages = getNumberOfPages(input_file)
        if total_pages <= 5:
            savePages(input_file, path, 1, total_pages, 1)
            return None

        nr_pages = 5
        last_page_index = 0
        while total_pages >= 5:
            try:
                last_page_index = savePages(input_file, path, last_page_index + 1, last_page_index + nr_pages,
                                            last_page_index)
                total_pages -= nr_pages
            except Exception as err:
                print(err)

        if total_pages > 0:
            savePages(input_file, path, last_page_index + 1, last_page_index + nr_pages, last_page_index)


if __name__ == '__main__':
    if (len(argv) != 2):
        print("Usage: convertPDF2img.py inputFile")
        exit(0)

    input_path = argv[1]
    convertToJPG(input_path)
