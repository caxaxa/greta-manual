import cv2
import numpy as np
import rasterio
import os




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

        # Convert the text position to a tuple of integers
        org = (x_pixel + 20, y_pixel + 10)
        # Convert the color tuple to integers
        color = (0, 10, 0)
        print(f'Annotating hotspots on panel : {key}')
        cv2.putText(image, str(key), org, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)  # Green color for numbers

    return image


def save_image_with_masks_and_numbers(blue_mask, red_mask, affected_panels_coord, ortho_path, output_path="output.png", debug =  False):
    """
    Save an image with the superposed masks on a white background and numbers over each affected panel.
    """
    # Create a white background of the same size as the blue_mask
    height, width = blue_mask.shape
    white_img = np.ones((height, width, 3), dtype=np.uint8) * 255  # 3 channels: Red, Green, Blue

    # Overlay the blue and red masks on the white image
    white_img[blue_mask == 255, :] = [10, 0, 0]  # Red for blue_mask
    white_img[red_mask == 255, :] = [0, 0, 255]   # Blue for red_mask
    print('Enumerating the Affected Panels on Layer Image')
    # Draw numbers directly on the white image with masks
    with rasterio.open(ortho_path) as dataset:
        white_img = draw_numbers_on_image(white_img, affected_panels_coord, dataset)

    if debug:
        import matplotlib.pyplot as plt
        def display_image(img, cmap=None, figsize=(10,10)):
            plt.figure(figsize=figsize)
            plt.imshow(img, cmap=cmap)
            plt.axis('off')
            plt.show()
        display_image(white_img)

    # Save the resulting image
    cv2.imwrite(output_path, white_img)

    return white_img


def create_maps(ortho_path, white_img, updated_df, report_dir):
    """
    Create an image with blue rectangles centered on the pixels given by the dataset column ['Coordenadas'].
    """
    for _, row in updated_df.iterrows():
        # Get geo-coordinates from DataFrame
        x_geo, y_geo = row['Coordenadas']

        # Convert geo-coordinates to pixel coordinates
        with rasterio.open(ortho_path) as dataset:
            x_pixel, y_pixel = geo_to_pixel(x_geo, y_geo, dataset)

        # Calculate rectangle dimensions (5% of the white_img dimensions)
        rect_width = int(0.15 * white_img.shape[1])
        rect_height = int(0.15 * white_img.shape[0])

        # Define top-left and bottom-right corners of the rectangle
        top_left = (x_pixel - rect_width // 2, y_pixel - rect_height // 2)
        bottom_right = (x_pixel + rect_width // 2, y_pixel + rect_height // 2)

        # Make a copy of the white_img for this specific entry
        img_copy = white_img.copy()

        # Draw rectangle on the img_copy
        cv2.rectangle(img_copy, top_left, bottom_right, (255, 0, 0), 5)  # Blue color

        # Construct the output filename based on 'Nome das Imagens'
        original_name = row['Nome das Imagens']
        output_name = original_name.replace('_MASKED.JPG', '_MAP.JPG')
        
        # Combine the report directory path with the output name
        output_path = os.path.join(report_dir, "report_images", output_name)
        
        # Save the modified img_copy
        cv2.imwrite(output_path, img_copy)

    return print('Maps Created Successfully')


