import numpy as np
import matplotlib.pyplot as plt
import scipy.misc
from skimage import color
from skimage import io
from skimage.io import imread
from sys import argv
from pprint import pprint
from PIL import Image



def denoise(img, output_path, weight=0.1, eps=1e-3, num_iter_max=200):
    u = np.zeros_like(img)
    px = np.zeros_like(img)
    py = np.zeros_like(img) 
    
    nm = np.prod(img.shape[:2])
    tau = 0.125
    
    i = 0
    while i < num_iter_max:
        u_old = u
        
        # x and y components of u's gradient
        ux = np.roll(u, -1, axis=1) - u
        uy = np.roll(u, -1, axis=0) - u
        
        # update the dual variable
        px_new = px + (tau / weight) * ux
        py_new = py + (tau / weight) * uy
        norm_new = np.maximum(1, np.sqrt(px_new **2 + py_new ** 2))
        px = px_new / norm_new
        py = py_new / norm_new

        # calculate divergence
        rx = np.roll(px, 1, axis=1)
        ry = np.roll(py, 1, axis=0)
        div_p = (px - rx) + (py - ry)
        
        # update image
        u = img + weight * div_p
        
        # calculate error
        error = np.linalg.norm(u - u_old) / np.sqrt(nm)
        
        if i == 0:
            err_init = error
            err_prev = error
        else:
            # break if error small enough
            if np.abs(err_prev - error) < eps * err_init:
                break
            else:
                e_prev = error
                
        # don't forget to update iterator
        i += 1
    scipy.misc.imsave(output_path, u)

if __name__=='__main__':
    if(len(argv)==4):
        input_path = argv[1]
        output_path = argv[2] 
        Weight=float(argv[3])
        image = Image.open(input_path).convert("L")
        arr = np.asarray(image)
        denoise(arr,output_path,Weight)
    elif(len(argv)==3):
        input_path = argv[1]
        output_path = argv[2] 
        Weight=65
        image = Image.open(input_path).convert("L")
        arr = np.asarray(image)
        denoise(arr,output_path,Weight)
    else:
        print("Usage: toBlakcWhite.py inputFile outputFile")
        exit(0)

