from PIL import Image
import numpy as scientific_computing
import imageio
import sys


def remove_noise(image_file, weight=0.1, epsilon=1e-3, maximum_number_of_iterations=200):
    u = scientific_computing.zeros_like(image_file)
    px = scientific_computing.zeros_like(image_file)
    py = scientific_computing.zeros_like(image_file)

    nm = scientific_computing.prod(image_file.shape[:2])
    tau = 0.125

    i = 0
    while i < maximum_number_of_iterations:
        u_old = u

        # x and y components of u's gradient
        ux = scientific_computing.roll(u, -1, axis=1) - u
        uy = scientific_computing.roll(u, -1, axis=0) - u

        # update the dual variable
        px_new = px + (tau / weight) * ux
        py_new = py + (tau / weight) * uy
        norm_new = scientific_computing.maximum(1, scientific_computing.sqrt(px_new ** 2 + py_new ** 2))
        px = px_new / norm_new
        py = py_new / norm_new

        # calculate divergence
        rx = scientific_computing.roll(px, 1, axis=1)
        ry = scientific_computing.roll(py, 1, axis=0)
        div_p = (px - rx) + (py - ry)

        # update image
        u = image_file + weight * div_p

        # calculate error
        error = scientific_computing.linalg.norm(u - u_old) / scientific_computing.sqrt(nm)

        if i == 0:
            err_init = error
            err_prev = error
        else:
            # if error is small enough break
            if scientific_computing.abs(err_prev - error) < epsilon * err_init:
                break
            else:
                err_prev = error

        # iterator increment
        i += 1

    return u


def get_array_from_image(image):
    return scientific_computing.asarray(image)


def open_image(image_path):
    return Image.open(image_path).convert("L")


def save_image(modified_image_array, image_path):
    image_path = image_path + 'result.png'
    imageio.imwrite(image_path, modified_image_array)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Invalid number of arguments. Usage: noiseRemove.py input-image-path output-image-path (noise-weight)")
        exit(-1)

    file_path = sys.argv[1]
    file_save_path = sys.argv[2]

    if len(sys.argv) == 4:
        noise_remove_weight = int(sys.argv[3])
    else:
        noise_remove_weight = 65

    unmodified_image = open_image(file_path)
    image_array = get_array_from_image(unmodified_image)
    noise_removed_image_array = remove_noise(image_array, weight=noise_remove_weight)
    save_image(noise_removed_image_array, file_save_path)

