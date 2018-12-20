from PIL import Image, ImageFilter, ImageOps
from threading import Thread
import sys
import imageio
import numpy
import time


def split_image(image):

    image = image.convert("L")

    image_array = get_array_from_image(image)
    width, height = image.size

    first_half_array = numpy.zeros((int(height / 2), width))

    for i in range(int(height / 2)):
        for j in range(width):
            first_half_array[i, j] = image_array[i, j]

    second_half_array = numpy.zeros((int(height / 2), width))

    for i in range(int(height / 2), height):
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


def median_filter(image, result, index):

    width, height = image.size

    filtered_image = image.copy()

    members = [(0, 0)] * 9

    for x in range(1, width - 1):
        for y in range(1, height - 1):

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

            filtered_image.putpixel((x - 1, y - 1), (members[4]))

    filtered_image.show()

    # result[index] = filtered_image


def median_filter_threads(image_path):

    threads = [None] * 2
    results = [None] * 2
    image_split = [None] * 2

    first_half_array, second_half_array, width, height = split_image(image_path)

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
    save_image("output_image.jpg", final_image_array)


def remove_unwanted_pixels_threads(image, weight=0.25):

    threads = [None] * 2
    results = [None] * 2
    image_split = [None] * 2

    first_half_array, second_half_array, width, height = split_image(image)

    image_split[0] = get_image_from_array(first_half_array)
    image_split[1] = get_image_from_array(second_half_array)

    image_split[0].show()

    for i in range(0, len(threads)):
        threads[i] = Thread(target=remove_unwanted_pixels, args=(image_split[i], weight, results, i))
        threads[i].start()

    for i in range(0, len(threads)):
        threads[i].join()

    first_half_array = get_array_from_image(results[0])
    second_half_array = get_array_from_image(results[1])

    final_image_array = reconstruct_image_as_array(first_half_array, second_half_array, width, height)
    final_image = get_image_from_array(final_image_array)

    final_image.show()


def remove_unwanted_pixels(image, frequency, result_object, thread_index):

    list_of_colors = image.getcolors()
    pixels = image.load()

    list_of_colors = sorted(list_of_colors, key=lambda x: x[0], reverse=True)

    width, height = image.size

    selected_colors = [x[1] for x in list_of_colors[0:int(len(list_of_colors) * frequency)]]

    for x in range(1, width):
        for y in range(1, height):
            if pixels[x, y] in selected_colors:
                pixels[x, y] = (255, 255, 255)

    image.show()

    # result_object[thread_index] = image


if __name__ == '__main__':
    start_time = time.time()

    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print("Check your parameters! Usage: python <source.py> <image_path> <weight>")
    else:

        image = Image.open(sys.argv[1])

        if len(sys.argv) == 2:
            remove_unwanted_pixels_threads(image, 0.25)
            # remove_unwanted_pixels(image, 0.25, None, None)
        else:
            remove_unwanted_pixels_threads(image, float(sys.argv[2]))

        ''' 
        image = Image.open("no_noise_part_1.jpg")

        inverted_image = ImageOps.invert(image)
        dilation_img = inverted_image.filter(ImageFilter.MaxFilter(3))
        erosion_img = dilation_img.filter(ImageFilter.MinFilter(5))
        erosion_img = ImageOps.invert(erosion_img)

        erosion_img.show()

        # process_image_threads("no_noise_part_1.jpg")
        # median_filter(image, None, None)
        '''
    print("Execution completed in %s seconds." % (time.time() - start_time))
