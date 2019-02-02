from pdf2image import convert_from_path
import tempfile
from sys import argv
import PyPDF2
import os


"""Get the total number of pages PDF contains
    :param path: the path to the PDF
    :returns the number of pages
"""
def getNumberOfPages(path):
    pdfFileObj = open(path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    nr = pdfReader.numPages
    pdfFileObj.close()

    return nr


"""Save pages from the interval [first_p, last_p] from PDF on disk
    :note: the name of the image is the prefix_id concatenated with "_" and the page number   
    :param input_file: the path to the PDF
    :param path: the path to the saved images
    :patam first_p: the number of the first page to be saved
    :param last_p: the number of the last page to be saved
    :param page_index: a contor to number the total pages saved
    :param prefix_id: the prefix of the image name to be saved
    :returns page_index + the number of the pages saved
"""
def savePages(input_file, path, first_p, last_p, page_index, prefix_id):
    pages = convert_from_path(input_file, dpi=100, output_folder=path,
                              thread_count=4,
                              fmt="JPEG", last_page=last_p, first_page=first_p)
    for page in pages:
        page_index += 1
        page.save("images/" + str(prefix_id) + "_" + str(page_index) + ".jpg")
    return page_index


"""Convert a PDF in JPEG images and save them on disk in ./images
    :note: the name of the image is the prefix_id concatenated with "_" and the page number
    :param input_file: the path to the PDF
    :param prefix_id: a string or integer that represents the prefix for the name of the saved images
    :returns the number of pages of the PDF
"""
def convertToJPG(input_file, prefix_id):
    with tempfile.TemporaryDirectory() as path:
        if os.path.exists("./images") == False:
            os.mkdir('./images')

        total_pages = getNumberOfPages(input_file)
        total = total_pages
        if total_pages <= 5:
            savePages(input_file, path, 1, total_pages, 0, prefix_id)
            return total_pages

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
    return total


"""Deletes the pages(images) saved on disk starting with page 1 until total_pages
    :note: used for cleanup
    :param prefix_id: the prefix of the image name
    :param total_pages: the number of the total pages to be deleted
"""
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
    print(convertToJPG(input_path, prefix_id))
