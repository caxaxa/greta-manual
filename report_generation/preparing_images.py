from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import shutil
import math

# Convert degree, minute, second to decimal format
def dms_to_decimal(dms, ref):
    degrees, minutes, seconds = dms
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return degrees + minutes/60.0 + seconds/3600.0

# Extract latitude and longitude from EXIF data
def get_lat_lon_from_exif(image_path):
    with Image.open(image_path) as img:
        exif_data = img._getexif()
        if not exif_data:
            return None
        
        geotagging = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif_data:
                    return None
                
                for (key, val) in GPSTAGS.items():
                    if key in exif_data[idx]:
                        geotagging[val] = exif_data[idx][key]
        
        if not geotagging:
            return None

        latitude = dms_to_decimal(geotagging['GPSLatitude'], geotagging['GPSLatitudeRef'])
        longitude = dms_to_decimal(geotagging['GPSLongitude'], geotagging['GPSLongitudeRef'])
        
        return (longitude, latitude)

# Compute the geodetic distance between two points using geopy
def euclidean_distance(coord1, coord2):
    """Compute the Euclidean distance between two points."""
    delta_x = coord1[0]- coord2[0]
    delta_y = coord1[1]- coord2[1]
    return math.sqrt(delta_x**2 + delta_y**2)

# Find the nearest image based on given coordinates
def get_nearest_image(coord, directory):
    min_distance = float('inf')
    nearest_image = None

    for image in os.listdir(directory):
        if image.endswith(('.JPG', '.jpg', '.png')):
            img_lat_lon = get_lat_lon_from_exif(os.path.join(directory, image))
            if not img_lat_lon:
                continue
            distance = euclidean_distance(img_lat_lon, coord)
            if distance < min_distance:
                min_distance = distance
                nearest_image = image

    return nearest_image

# Main function to process the dataframe and determine the nearest image
def locate_images_with_affected_panels(df):
    images_dir = os.path.join(os.getcwd(), "Inputs", "images")
    df['Nome das Imagens'] = df['Coordenadas Geográficas'].apply(lambda x: get_nearest_image(x, images_dir))
    return df

# Function to copy the relevant images to the report directory

def copy_images(df):
    current_directory = os.getcwd()
    
    # Paths for the current images
    src_images = os.path.join(current_directory, "Inputs", "images")
    src_raw_images = os.path.join(current_directory, "Inputs", "raw_images")
    dst_images = os.path.join(current_directory, "report", "report_images")
    
    # Path for ortho.png
    src_ortho = os.path.join(current_directory, "Inputs", "opensfm", "stats", "ortho.png")

    # Path for ortho.png
    top_view = os.path.join(current_directory, "Inputs", "opensfm", "stats", "topview.png")
    match = os.path.join(current_directory, "Inputs", "opensfm", "stats", "matchgraph.png")
    overlap = os.path.join(current_directory, "Inputs", "opensfm", "stats", "overlap.png")
    residual = os.path.join(current_directory, "Inputs", "opensfm", "stats", "residual_histogram.png")
    stats = os.path.join(current_directory, "Inputs", "opensfm", "stats", "stats.json")
    
    # Make sure the destination directory exists
    if not os.path.exists(dst_images):
        os.makedirs(dst_images)

    # Copy images from df
    for image in df['Nome das Imagens']:
        if not image:
            continue
        shutil.copy(os.path.join(src_images, image), dst_images)
        raw_image_name = image.replace('_MASKED', '_T')
        shutil.copy(os.path.join(src_raw_images, raw_image_name), dst_images)

    # Copy the ortho.png image
    shutil.copy(src_ortho, dst_images)
    shutil.copy(top_view, dst_images)
    shutil.copy(match, dst_images)
    shutil.copy(overlap, dst_images)
    shutil.copy(residual, dst_images)
    shutil.copy(stats, dst_images)


