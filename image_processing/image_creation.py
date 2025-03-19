
import numpy as np
import cv2
import rasterio
import matplotlib.pyplot as plt
import json
import os
from collections import defaultdict
import glob
import exifread
from PIL import Image
from rasterio.plot import reshape_as_image
import svgwrite


def annotate_and_downscale_orthophoto(
    ortho_path, 
    json_path, 
    output_path="ortho.png", 
    scale_factor=0.5
):
    """
    Annotates the orthophoto with defect locations (hotspots, faulty diodes, offline panels), 
    then downsizes the image.

    Args:
        ortho_path (str): Path to the orthophoto TIFF file.
        json_path (str): Path to the JSON file containing bounding boxes.
        output_path (str): Path to save the annotated and downscaled image.
        scale_factor (float): Factor to downscale the image (default: 0.5).
    """

    # Load JSON bounding boxes
    with open(json_path, "r") as f:
        data = json.load(f)
    
    bounding_boxes = data[0]["boundingBox"]["boundingBoxes"]

    # Load the TIFF image
    with rasterio.open(ortho_path) as src:
        ortho_img = np.moveaxis(src.read(), 0, -1).astype(np.uint8)  # Convert channels
        ortho_img = cv2.cvtColor(ortho_img, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format

    # Define colors for annotation
    color_map = {
        "hotspots": (0, 0, 255),      # Red
        "faultydiodes": (255, 0, 0),  # Blue
        "offlinepanels": (0, 255, 0)  # Green
    }

    # Annotate bounding boxes (ignore solar panels)
    for bbox in bounding_boxes:
        left, top, width, height = bbox["left"], bbox["top"], bbox["width"], bbox["height"]
        label = bbox["label"]

        if label == "solarpanels":
            continue  # Skip solar panels

        if label in color_map:
            color = color_map[label]

            # Draw bounding box
            cv2.rectangle(ortho_img, (left, top), (left + width, top + height), color, thickness=3)

            # Add label text
            text_pos = (left, top - 5)
            cv2.putText(
                ortho_img, label, text_pos,
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, lineType=cv2.LINE_AA
            )

    # Downscale the image
    downscaled_img = cv2.resize(ortho_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

    # Save the annotated orthophoto
    cv2.imwrite(output_path, downscaled_img)
    print(f"Annotated and downscaled orthophoto saved at {output_path}")



def generate_defect_map(
    tif_path,
    annotation_json_path,
    alignment='vertical',
    output_image="annotated_defects_map.svg",
    scale_factor=0.25
):
    """
    Reads bounding boxes from a JSON annotation file, draws panels and defects 
    onto a vector (SVG) canvas, and organizes them into a panel-level dictionary.
    
    In this version:
      - The final output is an SVG file (vectorized) that can be scaled in LaTeX.
      - Panel areas with any issues are filled with red at 50% opacity.
    
    Returns:
        panel_defects_dict: Nested dictionary with structure:
          {
              (col, row): {
                  "bbox": (x, y, w, h),
                  "hotspots": [ {...}, ...],
                  "faultydiodes": [...],
                  "offlinepanels": [...]
              },
              ...
          }
    """
    # --- Load image dimensions ---
    with rasterio.open(tif_path) as src:
        transform = src.transform
        img_h, img_w = src.height, src.width

    # --- Set up the SVG drawing ---
    # The viewBox remains at the original dimensions and the output size is scaled.
    scaled_w = int(img_w * scale_factor)
    scaled_h = int(img_h * scale_factor)
    dwg = svgwrite.Drawing(output_image, size=(f"{scaled_w}px", f"{scaled_h}px"),
                           viewBox=f"0 0 {img_w} {img_h}")
    # Add a white background
    dwg.add(dwg.rect(insert=(0, 0), size=(img_w, img_h), fill="white"))
    
    # --- Read JSON annotations ---
    with open(annotation_json_path, 'r') as f:
        data = json.load(f)
    
    # Flatten all bounding boxes from the JSON
    all_bboxes = []
    for item in data:
        if "boundingBox" in item and "boundingBoxes" in item["boundingBox"]:
            all_bboxes.extend(item["boundingBox"]["boundingBoxes"])
    
    # Separate bounding boxes by label (all lowercase)
    bboxes_by_label = defaultdict(list)
    for bb in all_bboxes:
        label = bb["label"].lower()
        left  = int(bb["left"])
        top   = int(bb["top"])
        w     = int(bb["width"])
        h     = int(bb["height"])
        # Create a 4-point contour
        contour = np.array([
            [left, top],
            [left + w, top],
            [left + w, top + h],
            [left, top + h]
        ], dtype=np.int32)
        bboxes_by_label[label].append(contour)
    
    # --- Extract panels and "defects" of interest ---
    default_panels = bboxes_by_label.get("default_panel", [])
    # These other labels are used later to assign defects to panels:
    hotspots      = bboxes_by_label.get("hotspots", [])
    faultydiodes  = bboxes_by_label.get("faultydiodes", [])
    offlinepanels = bboxes_by_label.get("offlinepanels", [])
    
    # --- Build bounding rectangles for each panel contour ---
    panel_bboxes = [cv2.boundingRect(cnt) for cnt in default_panels]  # Each is (x, y, w, h)
    
    # --- Sort panels into a grid (vertical or horizontal alignment) ---
    if alignment == 'vertical':
        panel_bboxes.sort(key=lambda b: (b[0], b[1]))
        cols = []
        current_col = [panel_bboxes[0]] if panel_bboxes else []
        for box in panel_bboxes[1:]:
            prev_box = current_col[-1]
            if abs(box[0] - prev_box[0]) > prev_box[2]:
                cols.append(current_col)
                current_col = [box]
            else:
                current_col.append(box)
        if current_col:
            cols.append(current_col)
        panel_grid = {}
        for col_idx, col in enumerate(cols):
            col_sorted = sorted(col, key=lambda b: b[1])
            for row_idx, box in enumerate(col_sorted):
                panel_grid[(col_idx+1, row_idx+1)] = box
    elif alignment == 'horizontal':
        panel_bboxes.sort(key=lambda b: (b[1], b[0]))
        rows = []
        current_row = [panel_bboxes[0]] if panel_bboxes else []
        for box in panel_bboxes[1:]:
            prev_box = current_row[-1]
            if abs(box[1] - prev_box[1]) > prev_box[3]:
                rows.append(current_row)
                current_row = [box]
            else:
                current_row.append(box)
        if current_row:
            rows.append(current_row)
        panel_grid = {}
        for row_idx, row in enumerate(rows):
            row_sorted = sorted(row, key=lambda b: b[0])
            for col_idx, box in enumerate(row_sorted):
                panel_grid[(row_idx+1, col_idx+1)] = box
    else:
        raise ValueError("alignment must be 'vertical' or 'horizontal'")
    
    # --- Build final dictionary: for each panel, store all relevant defects ---
    panel_defects_dict = {}
    for panel_key, panel_box in panel_grid.items():
        bx, by, bw, bh = panel_box  # boundingRect
        panel_defects_dict[panel_key] = {
            "bbox": (bx, by, bw, bh),
            "hotspots": [],
            "faultydiodes": [],
            "offlinepanels": []
        }
    
    # --- For each defect, find the nearest panel and add it to that panel’s list ---
    for defect_label in ["hotspots", "faultydiodes", "offlinepanels"]:
        for cnt in bboxes_by_label.get(defect_label, []):
            x, y, w, h = cv2.boundingRect(cnt)
            defect_center = (x + w/2, y + h/2)
            min_dist = float('inf')
            nearest_panel_key = None
            for key, box in panel_grid.items():
                bx, by, bw, bh = box
                panel_center = (bx + bw/2, by + bh/2)
                dist = np.hypot(defect_center[0] - panel_center[0],
                                defect_center[1] - panel_center[1])
                if dist < min_dist:
                    min_dist = dist
                    nearest_panel_key = key
            if nearest_panel_key is None:
                continue
            # Get geospatial centroid of the panel (if needed)
            panel_center_px = (panel_grid[nearest_panel_key][0] + panel_grid[nearest_panel_key][2]/2,
                               panel_grid[nearest_panel_key][1] + panel_grid[nearest_panel_key][3]/2)
            lon, lat = transform * panel_center_px
            panel_defects_dict[nearest_panel_key][defect_label].append({
                "bbox": (x, y, w, h),
                "defect_center_px": defect_center,
                "panel_center_px": panel_center_px,
                "panel_centroid_geospatial": (lon, lat)
            })
    
    # ---------------------
    # Draw vector elements into the SVG:
    # ---------------------
    
    # 1) Draw defect contours as filled polygons.
    defect_colors = {
        "hotspots": "red",
        "faultydiodes": "blue",
        "offlinepanels": "yellow"
    }
    for defect_label, color in defect_colors.items():
        for cnt in bboxes_by_label.get(defect_label, []):
            points = [(int(p[0]), int(p[1])) for p in cnt]
            dwg.add(dwg.polygon(points, fill=color, fill_opacity=1.0, stroke="none"))
    
    # 2) Draw panel outlines. If a panel has any defects, fill with red at 50% opacity; else, no fill.
    for panel_key, box in panel_grid.items():
        bx, by, bw, bh = box
        points = [(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh)]
        issues_count = (len(panel_defects_dict[panel_key]["hotspots"]) +
                        len(panel_defects_dict[panel_key]["faultydiodes"]) +
                        len(panel_defects_dict[panel_key]["offlinepanels"]))
        if issues_count > 0:
            fill_color = "red"
            fill_opacity = 0.5
            stroke_color = "red"
        else:
            fill_color = "none"
            fill_opacity = 0
            stroke_color = "black"
        dwg.add(dwg.polygon(points, fill=fill_color, fill_opacity=fill_opacity,
                            stroke=stroke_color, stroke_width=2))
    
    # 3) Label each panel (place text near the top-left).
    for panel_key, box in panel_grid.items():
        bx, by, bw, bh = box
        if alignment == 'vertical':
            label_str = f"{panel_key[0]}-{panel_key[1]}"
        else:
            label_str = f"{panel_key[1]}-{panel_key[0]}"
        dwg.add(dwg.text(label_str, insert=(bx, max(by - 5, 0)), fill="black", font_size="14px"))
    
    # Save the SVG (vector image)
    dwg.save()
    print(f"Annotated map saved as vector image to {output_image}")
    
    return panel_defects_dict




def annotate_and_crop_defect_area(
    tif_path,
    panel_defects_dict,
    layer_image_path,
    default_panel_width=127,
    crop_panel_size=5,  # in panel units
    output_dir="output_annotations",
    scale_factor=0.5
):
    """
    For each panel in `panel_defects_dict`, and for each defect type
    (hotspots, faultydiodes, offlinepanels) present in that panel:
      1. Finds the panel's bounding box,
      2. Creates an SVG vector "layer" image that shows a copy of the
         layer_image_path with a blue crop rectangle overlay,
      3. Creates a copy of the TIFF image that draws *only that defect type*
         for this panel,
      4. Crops around the panel center (using crop_panel_size * default_panel_width),
      5. Downscales and saves the cropped image as a JPEG.
      
    The layer image is saved with a filename like:
         "<defect_type>_(col-row)_layer.svg"
    and the cropped image is saved as:
         "<defect_type>_(col-row)_cropped.jpg"

    Returns:
        None. Saves images to `output_dir`.
    """
    os.makedirs(output_dir, exist_ok=True)

    # --- Load the original TIFF as an OpenCV image ---
    with rasterio.open(tif_path) as src:
        tif_img = reshape_as_image(src.read()).astype(np.uint8)  # (H, W, 3)
        tif_img = cv2.cvtColor(tif_img, cv2.COLOR_RGB2BGR)       # Convert to BGR
        tif_transform = src.transform

    # Color map for defect types
    color_map = {
        "hotspots":      (0, 0, 255),    # Red in BGR
        "faultydiodes":  (255, 0, 0),    # Blue
        "offlinepanels": (0, 255, 255)   # Yellow
    }
    defect_types = ["hotspots", "faultydiodes", "offlinepanels"]

    for panel_key, panel_info in panel_defects_dict.items():
        bx, by, bw, bh = panel_info["bbox"]
        panel_center_x = bx + bw // 2
        panel_center_y = by + bh // 2

        # Determine crop size
        half_size = (crop_panel_size * default_panel_width) // 2
        xmin = panel_center_x - half_size
        ymin = panel_center_y - half_size
        xmax = panel_center_x + half_size
        ymax = panel_center_y + half_size

        for defect_type in defect_types:
            defect_list = panel_info[defect_type]
            if len(defect_list) == 0:
                continue

            # -----------------------------
            # 1) Create a vector (SVG) layer image with a blue crop rectangle.
            # -----------------------------
            col_idx, row_idx = panel_key
            layer_filename = f"{defect_type}_({col_idx}-{row_idx})_layer.svg"
            layer_path = os.path.join(output_dir, layer_filename)
            
            # Try to get the dimensions of the layer image.
            layer_img_cv = cv2.imread(layer_image_path)
            if layer_img_cv is not None:
                h_layer, w_layer = layer_img_cv.shape[:2]
            else:
                h_layer, w_layer = tif_img.shape[:2]
            
            # Create an SVG drawing with the same coordinate system.
            dwg = svgwrite.Drawing(filename=layer_path, size=(w_layer, h_layer), viewBox=f"0 0 {w_layer} {h_layer}")
            # Embed the original layer image (referenced externally)
            dwg.add(dwg.image(href=layer_image_path, insert=(0, 0), size=(w_layer, h_layer)))
            # Draw the blue rectangle (no fill, stroke width 3)
            rect_width = xmax - xmin
            rect_height = ymax - ymin
            dwg.add(dwg.rect(insert=(xmin, ymin), size=(rect_width, rect_height),
                             stroke="blue", fill="none", stroke_width=3))
            dwg.save()

            # -----------------------------
            # 2) Annotate a copy of the TIFF with only this defect type.
            # -----------------------------
            annotated_tif = tif_img.copy()
            for defect_data in defect_list:
                dx, dy, dw, dh = defect_data["bbox"]
                contour = np.array([[dx, dy], [dx+dw, dy], [dx+dw, dy+dh], [dx, dy+dh]], dtype=np.int32)
                cv2.drawContours(annotated_tif, [contour], -1, color_map[defect_type], thickness=3)

            # -----------------------------
            # 3) Crop the annotated TIFF image.
            # -----------------------------
            crop_h = half_size * 2
            crop_w = half_size * 2
            cropped_img = np.ones((crop_h, crop_w, 3), dtype=np.uint8) * 255  # white background

            x1_crop = max(0, xmin)
            y1_crop = max(0, ymin)
            x2_crop = min(tif_img.shape[1], xmax)
            y2_crop = min(tif_img.shape[0], ymax)

            target_x1 = max(0, -xmin)
            target_y1 = max(0, -ymin)
            target_x2 = target_x1 + (x2_crop - x1_crop)
            target_y2 = target_y1 + (y2_crop - y1_crop)

            cropped_img[target_y1:target_y2, target_x1:target_x2] = \
                annotated_tif[y1_crop:y2_crop, x1_crop:x2_crop]

            # Name for the cropped image.
            cropped_filename = f"{defect_type}_({col_idx}-{row_idx})_cropped.jpg"
            cropped_path = os.path.join(output_dir, cropped_filename)
            # Downscale before saving.
            downscaled_img = cv2.resize(cropped_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
            cv2.imwrite(cropped_path, downscaled_img)
    
    print(f"Finished cropping by defect type. Saved results to '{output_dir}'.")


def process_and_rename_images(
    raw_images_dir,
    output_dir,
    panel_defects_dict,
    alignment='vertical',
    quality = 70
):
    """
    Creates exactly ONE image per panel & defect type.

    For each panel in `panel_defects_dict` and each defect type 
    ("hotspots", "faultydiodes", "offlinepanels"), if there is 
    at least one defect:
       1) Compute the average (lon, lat) of all such defects,
       2) Find the closest image (by lat/lon) in `raw_images_dir`,
       3) If that image is 'south'-oriented (see below), rotate 180°,
       4) Resize to half-size,
       5) Save as "<defect_type>_(col-row).jpg".

    Args:
        raw_images_dir (str): Path to .jpg images with EXIF GPS tags.
        output_dir (str): Where to save the processed images.
        panel_defects_dict (dict): Returned by generate_defect_map, e.g.
            {
              (14, 24): {
                "bbox": (...),
                "hotspots": [
                  {
                    "panel_centroid_geospatial": (lon, lat),
                    ...
                  },
                  ...
                ],
                "faultydiodes": [...],
                "offlinepanels": [...]
              },
              ...
            }
        alignment (str): 'vertical' or 'horizontal' (not actually used here, 
                         just included for API consistency).
    """

    os.makedirs(output_dir, exist_ok=True)

    # ----------------------------------------------------------------------
    # 1) Build metadata for .jpg images
    # ----------------------------------------------------------------------
    def tags_to_decimal(tags, ref):
        """Converts EXIF GPS tags [deg, min, sec] to decimal lat/lon."""
        try:
            deg, minutes, seconds = [
                float(str(x).split('/')[0]) / float(str(x).split('/')[1]) 
                if '/' in str(x) else float(x)
                for x in tags
            ]
        except:
            return None

        decimal = deg + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal *= -1
        return decimal

    def extract_metadata(img_path):
        """Reads EXIF lat/lon from an image file, returns {'lat':..., 'lon':...}."""
        with open(img_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

        lat_val = tags.get('GPS GPSLatitude')
        lat_ref = tags.get('GPS GPSLatitudeRef')
        lon_val = tags.get('GPS GPSLongitude')
        lon_ref = tags.get('GPS GPSLongitudeRef')

        if not (lat_val and lat_ref and lon_val and lon_ref):
            return {'lat': None, 'lon': None}

        lat = tags_to_decimal(lat_val.values, lat_ref.values)
        lon = tags_to_decimal(lon_val.values, lon_ref.values)
        return {
            'lat': lat if lat is not None else None,
            'lon': lon if lon is not None else None
        }

    metadata_dict = {}
    for jpg_path in glob.glob(os.path.join(raw_images_dir, '*.jpg')):
        fname = os.path.basename(jpg_path)
        metadata_dict[fname] = extract_metadata(jpg_path)

    # ----------------------------------------------------------------------
    # 2) Determine orientation per file ('south' or 'north' or None)
    # ----------------------------------------------------------------------
    def determine_orientation_by_filename(meta_dict):
        """
        Sorts images by filename alphabetically. For each file (except last),
        compare lat with next:
          - if next < current => 'south'
          - else => 'north'
        Last file => None
        """
        valid_entries = [
            (fname, coords['lat'])
            for fname, coords in meta_dict.items()
            if coords['lat'] is not None
        ]
        # Sort by filename
        valid_entries.sort(key=lambda x: x[0])

        orientation_map = {}
        for i in range(len(valid_entries)):
            current_fname, current_lat = valid_entries[i]
            if i == len(valid_entries) - 1:
                orientation_map[current_fname] = None
            else:
                _, next_lat = valid_entries[i + 1]
                if next_lat < current_lat:
                    orientation_map[current_fname] = 'south'
                else:
                    orientation_map[current_fname] = 'north'
        return orientation_map

    orientation_map = determine_orientation_by_filename(metadata_dict)

    # ----------------------------------------------------------------------
    # 3) Helper: find the closest .jpg to (lon, lat)
    # ----------------------------------------------------------------------
    def find_closest_image(lon, lat):
        """
        Return the filename with minimal distance in lat/lon space 
        to the defect coordinate (lon, lat).
        """
        min_dist = float('inf')
        closest_fname = None
        for fname, coords in metadata_dict.items():
            if coords['lat'] is None or coords['lon'] is None:
                continue
            # coords are (lat, lon). The defect is (lon, lat).
            d = np.hypot(coords['lat'] - lat, coords['lon'] - lon)
            if d < min_dist:
                min_dist = d
                closest_fname = fname
        return closest_fname

    # ----------------------------------------------------------------------
    # 4) For each panel & each defect type, create only ONE image
    # ----------------------------------------------------------------------
    all_defect_types = ["hotspots", "faultydiodes", "offlinepanels"]

    for panel_key, panel_data in panel_defects_dict.items():
        col_idx, row_idx = panel_key  # e.g. (14,24)

        for defect_type in all_defect_types:
            defects = panel_data[defect_type]
            if not defects:
                continue  # no defects of this type => skip

            # -------------------------
            # (A) Compute the average (lon, lat) of all defects of this type
            # -------------------------
            sum_lon, sum_lat = 0.0, 0.0
            for d in defects:
                lon, lat = d["panel_centroid_geospatial"]
                sum_lon += lon
                sum_lat += lat
            avg_lon = sum_lon / len(defects)
            avg_lat = sum_lat / len(defects)

            # -------------------------
            # (B) Find closest .jpg
            # -------------------------
            closest_fname = find_closest_image(avg_lon, avg_lat)
            if not closest_fname:
                print(f"[WARN] No matching image for {defect_type} in panel {panel_key}")
                continue

            src_path = os.path.join(raw_images_dir, closest_fname)
            if not os.path.isfile(src_path):
                print(f"[WARN] File not found: {src_path}")
                continue

            # -------------------------
            # (C) Open, rotate if south, resize
            # -------------------------
            img = Image.open(src_path)
            orientation = orientation_map.get(closest_fname, None)
            if orientation == 'south':
                img = img.rotate(180, expand=True)

            new_w = img.width // 2
            new_h = img.height // 2
            if new_w > 0 and new_h > 0:
                img = img.resize((new_w, new_h))

            # -------------------------
            # (D) Save as <defect_type>_(col-row).jpg
            # -------------------------
            new_name = f"{defect_type}_({col_idx}-{row_idx}).jpg"
            out_path = os.path.join(output_dir, new_name)
            img.save(out_path, quality=quality)
            print(f"[INFO] Saved => {new_name} (panel={panel_key}, type={defect_type})")

    print(f"[DONE] All processed images in '{output_dir}'.")




