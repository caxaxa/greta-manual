import cv2
import os
import matplotlib.pyplot as plt
from tifffile import imread

def load_orthophoto(path):
    # Read the tif file
    ortho_img = imread(path)

    ortho_img = cv2.cvtColor(ortho_img, cv2.COLOR_BGR2RGB)
    return ortho_img

def display_image(img, cmap=None, figsize=(10,10)):
    plt.figure(figsize=figsize)
    plt.imshow(img, cmap=cmap)
    plt.axis('off')
    plt.show()
    
def get_single_file_in_directory(directory_path):
    """
    Check if there is only one file in the given directory and return its name.
    If there are multiple files or no files, return False.
    """
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    if len(files) == 1:
        return files[0]
    else:
        return False
