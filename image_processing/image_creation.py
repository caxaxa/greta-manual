import cv2
import numpy as np
import rasterio

def geo_to_pixel(x_geo, y_geo, dataset):
    """
    Convert geo-coordinates to pixel coordinates using the affine transformation of the dataset.
    """
    x_pixel, y_pixel = ~dataset.transform * (x_geo, y_geo)
    return round(x_pixel), round(y_pixel)


def draw_numbers_on_image(image, affected_panels_coord, dataset):
    """
    Draw numbers over each affected panel on the given image.
    """
    for key, (x_geo, y_geo) in affected_panels_coord.items():
        x_pixel, y_pixel = geo_to_pixel(x_geo, y_geo, dataset)
        cv2.putText(image, str(key), (x_pixel + 20, y_pixel + 10 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 10, 0), 1, cv2.LINE_AA)  # Green color for numbers

    return image

def save_image_with_masks_and_numbers(blue_mask, red_mask, affected_panels_coord, ortho_path, output_path="output.png"):
    """
    Save an image with the superposed masks on a white background and numbers over each affected panel.
    """
    # Create a white background of the same size as the blue_mask
    height, width = blue_mask.shape
    white_img = np.ones((height, width, 3), dtype=np.uint8) * 255  # 3 channels: Red, Green, Blue

    # Overlay the blue and red masks on the white image
    white_img[blue_mask == 255, :] = [10, 0, 0]  # Red for blue_mask
    white_img[red_mask == 255, :] = [0, 0, 255]   # Blue for red_mask

    # Draw numbers directly on the white image with masks
    with rasterio.open(ortho_path) as dataset:
        white_img = draw_numbers_on_image(white_img, affected_panels_coord, dataset)

    # Save the resulting image
    cv2.imwrite(output_path, white_img)
