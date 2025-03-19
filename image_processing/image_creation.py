
import numpy as np
import cv2
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import reshape_as_image
import json
import os



def generate_defect_map(
    tif_path, 
    contours_by_label, 
    alignment='vertical', 
    output_image="annotated_defects_map.jpg"
):
    with rasterio.open(tif_path) as src:
        transform = src.transform
        img_h, img_w = src.height, src.width

    # Create white background
    canvas = np.full((img_h, img_w, 3), 255, dtype=np.uint8)


    # Draw panels as reference
    default_panels = contours_by_label.get("default_panel", [])
    defects = (contours_by_label.get("hotspots", []) + 
               contours_by_label.get("faultydiodes", []) +
               contours_by_label.get("offlinepanels", []))

    # Draw default panels in black (redundant on black bg but for completeness)
    for cnt in default_panels:
        cv2.drawContours(canvas, [cnt], -1, (0, 0, 0), thickness= 2 )

    # Colors for defects
    colors = {
        "hotspots": (0, 0, 255),      # Red
        "faultydiodes": (255, 0, 0),  # Blue
        "offlinepanels": (0, 255, 255) # Yellow
    }

    # Draw defects
    for label in ["hotspots", "faultydiodes", "offlinepanels"]:
        for cnt in contours_by_label.get(label, []):
            cv2.drawContours(canvas, [cnt], -1, colors[label], thickness=cv2.FILLED)

    # Organize panels into columns or rows
    panel_bboxes = [cv2.boundingRect(cnt) for cnt in default_panels]

    # Sorting panels for alignment
    if alignment == 'vertical':
        # Sort horizontally first (columns), then vertically
        panel_bboxes.sort(key=lambda b: (b[0], b[1]))
        # Find column breaks based on horizontal gaps
        cols = []
        current_col = [panel_bboxes[0]]
        for box in panel_bboxes[1:]:
            prev_box = current_col[-1]
            if abs(box[0] - prev_box[0]) > box[2]:  # Column break
                cols.append(current_col)
                current_col = [box]
            else:
                current_col.append(box)
        cols.append(current_col)

        panel_grid = {(col_idx+1, row_idx+1): box 
                      for col_idx, col in enumerate(cols) 
                      for row_idx, box in enumerate(sorted(col, key=lambda b: b[1]))}

    elif alignment == 'horizontal':
        # Sort vertically first (rows), then horizontally
        panel_bboxes.sort(key=lambda b: (b[1], b[0]))
        rows = []
        current_row = [panel_bboxes[0]]
        for box in panel_bboxes[1:]:
            prev_box = current_row[-1]
            if abs(box[1] - prev_box[1]) > box[3]:  # Row break
                rows.append(current_row)
                current_row = [box]
            else:
                current_row.append(box)
        rows.append(current_row)

        panel_grid = {(row_idx+1, col_idx+1): box 
                      for row_idx, row in enumerate(rows) 
                      for col_idx, box in enumerate(sorted(row, key=lambda b: b[0]))}
    else:
        raise ValueError("alignment must be 'vertical' or 'horizontal'")

    # Find nearest panel for each defect
    defects_dict = {}
    for label in ["hotspots", "faultydiodes"]:
        for cnt in contours_by_label.get(label, []):
            x, y, w, h = cv2.boundingRect(cnt)
            defect_center = (x + w / 2, y + h / 2)

            # Find closest panel centroid
            min_dist = float('inf')
            nearest_panel_key = None
            for key, box in panel_grid.items():
                bx, by, bw, bh = box
                panel_center = (bx + bw / 2, by + bh / 2)
                dist = np.hypot(defect_center[0] - panel_center[0], defect_center[1] - panel_center[1])
                if dist < min_dist:
                    min_dist = dist
                    nearest_panel_key = key

            # Label on image
            if alignment == 'vertical':
                label_str = f"{nearest_panel_key[0]}-{nearest_panel_key[1]}"
            else:
                label_str = f"{nearest_panel_key[1]}-{nearest_panel_key[0]}"

            # Place text label near defect
            text_pos = (int(x + w + 5), int(y + h / 2))
            cv2.putText(canvas, label_str, text_pos, 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

            # Geospatial centroid of the panel
            panel_box = panel_grid[nearest_panel_key]
            panel_center_px = panel_box[0] + panel_box[2]/2, panel_box[1] + panel_box[3]/2
            lon, lat = transform * panel_center_px

            defects_dict[label_str] = {
                "issue_type": label,
                "panel_centroid_geospatial": [lon, lat]
            }

    # Save annotated map
    cv2.imwrite(output_image, canvas)
    print(f"Annotated map saved to {output_image}")

    # # Display the image
    # plt.figure(figsize=(10,10))
    # plt.imshow(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    # plt.title("Annotated Defects Map")
    # plt.axis("off")
    # plt.show()

    # # Return the dictionary of defects
    # with open("defects_labels.json", "w") as f:
    #     json.dump(defects_dict, f, indent=2)

    # print("Defect labels and coordinates saved to defects_labels.json")
    return defects_dict


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
