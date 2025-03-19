import os
import glob
import exifread
import rasterio
import numpy as np
from PIL import Image
from rasterio.plot import reshape_as_image
import cv2

def process_and_rename_images(
    raw_images_dir,
    output_dir,
    defects_dict,
    alignment='vertical'
):
    """
    Reads images from `raw_images_dir`, extracts their GPS metadata,
    determines an overall orientation (north/south) by comparing
    the top two latitudes, rotates if needed, then resizes and saves
    images based on the defect information in `defects_dict`.
    """
    os.makedirs(output_dir, exist_ok=True)

    # ----------------------------------------------------------------------
    # Helper functions embedded here for simplicity
    # ----------------------------------------------------------------------

    def tags_to_decimal(tags, ref):
        """Converts EXIF GPS tags to decimal lat/lon."""
        # Each GPS coordinate component can appear as 'num/den', so parse accordingly
        deg, minutes, seconds = [
            float(str(x).split('/')[0]) / float(str(x).split('/')[1]) 
            if '/' in str(x) else float(x)
            for x in tags
        ]
        decimal = deg + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal *= -1
        return decimal

    def extract_metadata(image_path):
        """Reads the file EXIF tags and returns a dict with lat/lon."""
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

            lat_val = tags.get('GPS GPSLatitude')
            lat_ref = tags.get('GPS GPSLatitudeRef')
            lon_val = tags.get('GPS GPSLongitude')
            lon_ref = tags.get('GPS GPSLongitudeRef')

            if not (lat_val and lat_ref and lon_val and lon_ref):
                # If GPS data is missing, you might want to skip or handle differently
                return {'lat': None, 'lon': None}

            lat = tags_to_decimal(lat_val.values, lat_ref.values)
            lon = tags_to_decimal(lon_val.values, lon_ref.values)

        return {'lat': lat, 'lon': lon}

    def build_image_metadata_dict(directory):
        """Builds a {filename: {'lat': ..., 'lon': ...}} dict from images."""
        metadata_dict = {}
        for img_path in glob.glob(os.path.join(directory, '*.jpg')):
            md = extract_metadata(img_path)
            metadata_dict[os.path.basename(img_path)] = md
        return metadata_dict

    def determine_orientation_by_filename(metadata_dict):
        """
        Sort images by name. For each image (except the last),
        compare its latitude to the next image's latitude:
        - If next < current: 'south'
        - else: 'north'
        For the last file in the list, return None.
        """

        # 1. Gather only entries with a valid latitude
        valid_entries = [(fname, coords['lat'])
                        for fname, coords in metadata_dict.items()
                        if coords['lat'] is not None]

        # 2. Sort them by filename in ascending order
        valid_entries.sort(key=lambda x: x[0])  # x[0] is the filename

        # 3. Build a result dictionary: {filename -> 'south' / 'north' / None}
        orientation_map = {}
        for i in range(len(valid_entries)):
            current_fname, current_lat = valid_entries[i]

            if i == len(valid_entries) - 1:
                # It's the last file, so there's no "next" => orientation = None
                orientation_map[current_fname] = None
            else:
                # Compare with the next file's latitude
                _, next_lat = valid_entries[i + 1]
                if next_lat < current_lat:
                    orientation_map[current_fname] = 'south'
                else:
                    orientation_map[current_fname] = 'north'

        return orientation_map


    def find_closest_image(metadata_dict, defect_coord):
        """
        Find the image whose lat/lon is nearest to the provided
        (lon, lat) defect_coord using Euclidean distance in lat/lon space.
        defect_coord is a tuple: (longitude, latitude)
        """
        min_dist = float('inf')
        closest_img = None

        for img_name, coords in metadata_dict.items():
            if coords['lat'] is None or coords['lon'] is None:
                continue
            # coords in metadata_dict are (lat, lon) but our defect is (lon, lat)
            dist = np.hypot(coords['lat'] - defect_coord[1], coords['lon'] - defect_coord[0])
            if dist < min_dist:
                min_dist = dist
                closest_img = img_name

        return closest_img

    # ----------------------------------------------------------------------
    # Main logic
    # ----------------------------------------------------------------------

    # 1. Build a metadata dict for all images in raw_images_dir
    metadata_dict = build_image_metadata_dict(raw_images_dir)



    # 2. Determine overall orientation
    orientation = determine_orientation_by_filename(metadata_dict)
    print(f"Detected image orientation: {orientation}")

    # 3. Process each defect entry
    for label, defect_info in defects_dict.items():
        lon, lat = defect_info["panel_centroid_geospatial"]
        issue_type = defect_info["issue_type"]

        # 3a. Find the closest image based on defect coordinates
        closest_img = find_closest_image(metadata_dict, (lon, lat))
        if closest_img is None:
            # If no matching GPS data, skip or handle differently
            print(f"No matching image found for {label}")
            continue

        original_img_path = os.path.join(raw_images_dir, closest_img)
        img = Image.open(original_img_path)

        # 3b. If orientation is 'south', rotate the entire image 180
        if orientation == 'south':
            img = img.rotate(180, expand=True)

        # 3c. Resize the image (e.g., half size)
        img = img.resize((img.width // 2, img.height // 2))

        # 3d. Save with a new name: <issue_type>_<label>.jpg
        new_filename = f"{issue_type}_{label}.jpg"
        save_path = os.path.join(output_dir, new_filename)
        img.save(save_path, quality=90)

        print(f"Processed and saved: {new_filename}")




def annotate_and_crop_defect_area(
    tif_path,
    defects_dict,
    contours_by_label,  # NEW: Contours extracted from JSON
    layer_image_path,
    default_panel_width=127,
    crop_panel_size=5,
    output_dir="output_annotations"
):
    os.makedirs(output_dir, exist_ok=True)

    # Load the TIFF image
    with rasterio.open(tif_path) as src:
        tif_img = reshape_as_image(src.read()).astype(np.uint8)  # Ensure correct format
        tif_img = cv2.cvtColor(tif_img, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format
        tif_transform = src.transform

    half_size = (crop_panel_size * default_panel_width) // 2

    for label, defect in defects_dict.items():
        lon, lat = defect["panel_centroid_geospatial"]
        issue_type = defect["issue_type"]

        # Convert geospatial centroid to pixel coordinates
        px, py = ~tif_transform * (lon, lat)
        px, py = int(px), int(py)

        xmin, ymin = px - half_size, py - half_size
        xmax, ymax = px + half_size, py + half_size

        # Load the layer image (fresh copy per defect)
        annotated_layer = cv2.imread(layer_image_path)

        # Annotate rectangle on the layer image
        cv2.rectangle(
            annotated_layer,
            (xmin, ymin),
            (xmax, ymax),
            (255, 0, 0), 3  # Blue box
        )

        # Save individual annotated map
        annotated_map_filename = f"{issue_type}_{label}_map.jpg"
        cv2.imwrite(os.path.join(output_dir, annotated_map_filename), annotated_layer)

        # Copy original TIFF image before cropping
        annotated_tif = tif_img.copy()

        # **Annotate defects directly on the TIFF image before cropping**
        for defect_type in ["hotspots", "faultydiodes"]:
            if defect_type in contours_by_label:
                for contour in contours_by_label[defect_type]:
                    cv2.drawContours(
                        annotated_tif,
                        [np.array(contour, dtype=np.int32)],
                        -1,
                        (0, 0, 255),  # **Red color**
                        thickness=3
                    )

        # Crop from annotated TIFF with padding if exceeding bounds
        crop_h, crop_w = half_size * 2, half_size * 2
        cropped_img = np.ones((crop_h, crop_w, 3), dtype=np.uint8) * 255  # White background

        x1_crop, y1_crop = max(0, xmin), max(0, ymin)
        x2_crop, y2_crop = min(tif_img.shape[1], xmax), min(tif_img.shape[0], ymax)

        # Coordinates to place crop correctly
        target_x1, target_y1 = max(0, -xmin), max(0, -ymin)
        target_x2, target_y2 = target_x1 + (x2_crop - x1_crop), target_y1 + (y2_crop - y1_crop)

        # Apply crop
        cropped_img[target_y1:target_y2, target_x1:target_x2] = annotated_tif[y1_crop:y2_crop, x1_crop:x2_crop]

        # Save cropped image
        cropped_img_filename = f"{issue_type}_{label}_cropped.jpg"
        cv2.imwrite(os.path.join(output_dir, cropped_img_filename), cropped_img)

    print(f"All defect crops and maps saved to {output_dir}")

