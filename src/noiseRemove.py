import time
import sys
import os

import imageio
import numpy
import cv2
from PIL import Image, ImageEnhance, ImageFilter

from threading import Thread

import imageio.core.util

def silence_imageio_warning(*args, **kwargs):
    pass

imageio.core.util._precision_warn = silence_imageio_warning

def split_image(image):

    image = image.convert("L")

    image_array = get_array_from_image(image)
    width, height = image.size

    first_half_array = numpy.zeros((int(height / 2), width))

    for i in range(int(height / 2)):
        for j in range(width):
            first_half_array[i, j] = image_array[i, j]

    second_half_array = numpy.zeros((int(height / 2), width))

    for i in range(int(height / 2), height - 1):
        for j in range(width):
            second_half_array[int(height / 2) + 1 - i, j] = image_array[i, j]

    return first_half_array, second_half_array, width, height


def reconstruct_image_as_array(first_half_array, second_half_array, columns, rows):

    image_array = numpy.zeros((rows, columns))

    for i in range(int(rows / 2)):
        for j in range(columns):
            image_array[i, j] = first_half_array[i, j]

    for i in range(int(rows / 2), rows):
        for j in range(columns):
            image_array[i, j] = second_half_array[int(rows / 2) + 1 - i, j]

    return image_array


def get_image_from_array(image_array):

    image = Image.fromarray(image_array)
    return image


def get_array_from_image(image):

    image_array = numpy.asarray(image)
    return image_array


def save_image(output_image_name, image_array):

    imageio.imwrite(output_image_name, image_array)


def open_image(image_path):
    return Image.open(image_path)


def median_filter(image, result, index):

    width, height = image.size

    filtered_image = image.copy()

    members = [(0, 0)] * 9

    for x in range(1, width - 1, 4):
        for y in range(1, height - 1, 4):

            members[0] = image.getpixel((x - 1, y - 1))
            members[1] = image.getpixel((x - 1, y))
            members[2] = image.getpixel((x - 1, y + 1))
            members[3] = image.getpixel((x, y - 1))
            members[4] = image.getpixel((x, y))
            members[5] = image.getpixel((x, y + 1))
            members[6] = image.getpixel((x + 1, y - 1))
            members[7] = image.getpixel((x + 1, y))
            members[8] = image.getpixel((x + 1, y + 1))

            members.sort()

            filtered_image.putpixel((x, y), (members[4]))

    #filtered_image.show()
    result[index] = filtered_image


def median_filter_threads(image):

    threads = [None] * 2
    results = [None] * 2
    image_split = [None] * 2

    first_half_array, second_half_array, width, height = split_image(image)

    image_split[0] = get_image_from_array(first_half_array)
    image_split[1] = get_image_from_array(second_half_array)

    for i in range(0, len(threads)):
        threads[i] = Thread(target=median_filter, args=(image_split[i], results, i))
        threads[i].start()

    for i in range(0, len(threads)):
        threads[i].join()

    first_half_array = get_array_from_image(results[0])
    second_half_array = get_array_from_image(results[1])

    final_image_array = reconstruct_image_as_array(first_half_array, second_half_array, width, height)
    save_image("output_image_no_noise.jpg", final_image_array)


def remove_unwanted_pixels_threads(image, frequency=0.1):

    threads = [None] * 2
    results = [None] * 2
    image_split = [None] * 2

    first_half_array, second_half_array, width, height = split_image(image)

    image_split[0] = get_image_from_array(first_half_array)
    image_split[1] = get_image_from_array(second_half_array)

    for i in range(0, len(threads)):
        threads[i] = Thread(target=remove_unwanted_pixels, args=(image_split[i], results, i, frequency))
        threads[i].start()

    for i in range(0, len(threads)):
        threads[i].join()

    first_half_array = get_array_from_image(results[0])
    second_half_array = get_array_from_image(results[1])

    final_image_array = reconstruct_image_as_array(first_half_array, second_half_array, width, height)
    save_image("output_image_no_pixels.jpg", final_image_array)


def remove_unwanted_pixels(image_to_process, result_object, thread_index, frequency=0.1):

    list_of_colors = image_to_process.getcolors()
    pixels = image_to_process.load()
    list_of_colors = sorted(list_of_colors, key=lambda x: x[0], reverse=True)
    selected_colors = [x[1] for x in list_of_colors[0:int(len(list_of_colors) * frequency)]]

    width, height = image_to_process.size

    for x in range(1, width):
        for y in range(1, height):
            if pixels[x, y] in selected_colors:
                pixels[x, y] = 255.0

    result_object[thread_index] = image_to_process


def posteriorizate(image_path, level):

    image_to_process = cv2.imread(image_path)
    color_list = numpy.arange(0, 256)
    divider = numpy.linspace(0, 255, level + 1)[1]
    quantization_colors = numpy.int0(numpy.linspace(0, 255, level)) 
    color_levels = numpy.clip(numpy.int0(color_list / divider), 0, level - 1)
    palette = quantization_colors[color_levels]
    processed_image = palette[image_to_process]
    processed_image = cv2.convertScaleAbs(processed_image)

    cv2.imwrite("output_image.jpg", processed_image)


def cleanup():
    if os.path.exists("output_image_levels.jpg"):
        os.remove("output_image_levels.jpg")
    if os.path.exists("output_image_no_noise.jpg"):
        os.remove("output_image_no_noise.jpg")
    if os.path.exists("output_image_no_pixels.jpg"):
        os.remove("output_image_no_pixels.jpg")


def remove_noise(image):
    median_filter_threads(image)
    remove_unwanted_pixels_threads(open_image("output_image_no_noise.jpg"), 0.05)
    posteriorizate("output_image_no_pixels.jpg", 2)
    cleanup()
    return open_image("output_image.jpg")



if __name__ == '__main__':

    # start_time = time.time()

    if len(sys.argv) != 2:
        print("Check your parameters! Usage: python <source.py> <image_path>")
    else:
        median_filter_threads(open_image(sys.argv[1]))
        remove_unwanted_pixels_threads(open_image("output_image_no_noise.jpg"), 0.05)
        posteriorizate("output_image_no_pixels.jpg", 2)
        cleanup()

    # print("Execution completed in %s seconds." % (time.time() - start_time))
