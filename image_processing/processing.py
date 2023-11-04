import cv2
import numpy as np
import rasterio

#enable for diyplaying and debugging


def remove_large_horizontal_segments(matrix):
    # Output matrix, initially a copy of the original matrix
    
    output_matrix = np.copy(matrix)

    # Store zero segments (start, end) for each row
    zero_segments = []

    # Iterate through each row to find zero segments
    for row_idx in range(matrix.shape[0]):
        row = matrix[row_idx, :]

        # Skip rows that are entirely zeros or 255
        if np.all(row == 0) or np.all(row == 255):
            continue

        # Identify zero segments
        zero_segment = []
        count = 0
        start_idx = 0
        for col_idx in range(matrix.shape[1]):
            if row[col_idx] == 0:
                if count == 0:
                    start_idx = col_idx
                count += 1
            else:
                if count > 0:
                    zero_segment.append((start_idx, col_idx))
                count = 0
        # If the row ends with a zero segment, include it
        if count > 0:
            zero_segment.append((start_idx, matrix.shape[1]))
        # Update zero_segments with the segments for this row
        zero_segments.extend(zero_segment)
    # Find the largest zero segment
    max_length = max(end - start for start, end in zero_segments)
    # Erase corresponding parts of 255-only rows
    for row_idx in range(matrix.shape[0]):
        row = matrix[row_idx, :]

        # Only target rows that are entirely 255
        if np.all(row == 255):
            non_erasable_found = False
            for start, end in zero_segments:
                length = end - start
                if length >= 0.6 * max_length:  # The5 10% rule
                    output_matrix[row_idx, start:end] = 0
                    non_erasable_found = True
                else:
                    # Edge cases
                    if start == 0 and non_erasable_found:
                        output_matrix[row_idx, start:end] = 0
                    if end == matrix.shape[1] and non_erasable_found:
                        output_matrix[row_idx, start:end] = 0

    return output_matrix

def create_masks_from_orthophoto(img, debug =  False):

    ortho_img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Blue and Red HSV ranges 
    blue_lower = np.array([110, 110, 100])
    blue_upper = np.array([140, 255, 255])
    red_lower = np.array([0, 100, 100])
    red_upper = np.array([50, 255, 255])


    # Create masks for blue and red colors
    # red mask treated trhough HSV, blue mask not
    blue_mask = cv2.inRange(ortho_img_HSV, blue_lower, blue_upper)
    red_mask = cv2.inRange(ortho_img_HSV, red_lower, red_upper)

    print(f'Created bluemask with shape {blue_mask.shape} and values {np.unique(blue_mask)}')
    print(f'Created redmask with shape {red_mask.shape} and values {np.unique(red_mask)}')

    # Create a black image with the same size as the mask images

    # Find contours in the blue and red masks
    # Define a kernel for dilation
    kernel_size_blue = 2  # Adjust as needed for the desired thickness
    kernel_blue = np.ones((kernel_size_blue, kernel_size_blue), np.uint8)

    # Define a kernel for dilation
    kernel_size_red = 10  # Adjust as needed for the desired thickness
    kernel_red = np.ones((kernel_size_red, kernel_size_red), np.uint8)

    # Dilate the blue mask to thicken the lines
    blue_mask = cv2.dilate(blue_mask, kernel_blue, iterations=1)
    red_mask = cv2.dilate(red_mask, kernel_red, iterations=1)

    if debug:
        import matplotlib.pyplot as plt
        def display_image(img, cmap=None, figsize=(10,10)):
            plt.figure(figsize=figsize)
            plt.imshow(img, cmap=cmap)
            plt.axis('off')
            plt.show()
        display_image(blue_mask)
        display_image(red_mask)


    print('Finding upper and lower bounds')
    # Get shapes and set initial variables to calculate bounds
    (rows, cols) = blue_mask.shape
    upper_bound = 0
    lower_bound = rows - 1

    zero_row_found = False  # Flag for when a zero row is found

    # Find the upper bound
    for i in range(rows):
        row = blue_mask[i, :]
        num_zeros = np.count_nonzero(row == 0)

        if num_zeros > 0.99 * cols:
            zero_row_found = True
            continue

        if zero_row_found and np.count_nonzero(row) > 0.1 * cols:
            upper_bound = i
            break

    zero_row_found = False  # Reset flag for lower bound search

    print(f'found upperbound at pixel {upper_bound} ')

    # Find the lower bound
    for i in range(rows - 1, -1, -1):
        row = blue_mask[i, :]
        num_zeros = np.count_nonzero(row == 0)

        if num_zeros > 0.99 * cols:
            zero_row_found = True
            continue

        if zero_row_found and np.count_nonzero(row) > 0.1 * cols:
            lower_bound = i
            break

    print(f'found upperbound at pixel {lower_bound} ')   
        
    tolerance = 0.2  # If picture is too much blueish use higher value --> 23%
    # Draw horizontal lines between upper_bound and lower_bound where applicable
    for i in range(rows):
        row = blue_mask[i, :]
        if np.count_nonzero(row) > tolerance * cols:
            cv2.line(blue_mask, (0, i), (cols, i), 255, 1)  # Draw horizontal line on blue_mask

    # Draw vertical lines between left_bound and right_bound where applicable
    for j in range(cols):
        col = blue_mask[:, j]
        if np.count_nonzero(col) > tolerance * rows:
            cv2.line(blue_mask, (j, 0), (j, rows), 255, 1)  # Draw vertical line on blue_mask

    # Identify rows where every element is non-zero, only between upper_bound and lower_bound
    all_non_zero_rows = [np.all(blue_mask[i, :]) for i in range(rows)]

    # Identify columns where every element is non-zero
    all_non_zero_cols = [np.all(blue_mask[:, j]) for j in range(cols)]

    # Zero out elements not in those rows or columns, only between upper_bound and lower_bound
    for i in range(rows):
        for j in range(cols):
            if not (all_non_zero_rows[i] or all_non_zero_cols[j]):
                blue_mask[i, j] = 0


    # Zero out everything above and below the bounds in both masks
    blue_mask[:upper_bound, :] = 0
    blue_mask[lower_bound+1:, :] = 0
    red_mask[:upper_bound, :] = 0
    red_mask[lower_bound+1:, :] = 0

    # # Draw red lines at the boundaries on the blue_mask
    cv2.line(blue_mask, (0, upper_bound), (cols, upper_bound), (255), 1)
    cv2.line(blue_mask, (0, lower_bound), (cols, lower_bound), (255), 1)

    kernel_size = 5
    kernel = np.ones((kernel_size, kernel_size), np.uint8)

    # Perform dilation followed by erosion to close gaps. This is also known as "Closing"
    dilated = cv2.dilate(blue_mask, kernel, iterations=5)
    closed = cv2.erode(dilated, kernel, iterations=5)

    blue_mask = closed

    print('Blue Mask Processed')
    print('Red Mask Processed')

    if debug:
        display_image(blue_mask)
        display_image(red_mask)

    new_mask = remove_large_horizontal_segments(blue_mask)

    print('Trackers defined for the Blue Mask')

    #display bluemask for debuggig

    if debug:
        display_image(new_mask)



    # Assume red_mask is your binary mask image with values 0 and 255

    # Find contours
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an output image, same size and type as red_mask but filled with zeros (i.e., all black)
    output = np.zeros_like(red_mask)

    # Initialize a variable to hold the sum of all lengths
    total_length = 0
    total_count = 0

    # Calculate the average length
    for contour in contours:
        total_length += cv2.arcLength(contour, True)
        total_count += 1
    if total_count == 0:
        print("No contours found.")
        exit()

    average_length = int(total_length / total_count)
    radius = int(average_length / 8)  # Radius can be adjusted as per your requirement

    # Draw filled circles
    for contour in contours:
        # Calculate the moments of the contour to find the center point
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # Draw a filled circle at the center point
        cv2.circle(output, (cX, cY), radius, (255), -1)

    # Now, 'output' contains your final image with filled circles
    red_mask = output

    print('Hotspots defined for the Red Mask')

    if debug:
        display_image(red_mask)

    return new_mask , red_mask
        

def generate_affected_panels_coordinates(tif_path, blue_mask, red_mask):
    def detect_contours(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    with rasterio.open(tif_path) as dataset:
        transform = dataset.transform  # Get the transformation matrix
    affected_panels_coordinate = {}
    trackers = detect_contours(blue_mask)
    trackers = sorted(trackers, key=lambda c: cv2.boundingRect(c)[0])
    hotspots = detect_contours(red_mask)
    used_hotspots = set()

    def _convert_to_geo_coordinates(contour, x_offset=0, y_offset=0):
        return [((pt[0][0] + x_offset) * transform[0] + transform[2],
                (pt[0][1] + y_offset) * transform[4] + transform[5]) for pt in contour]

    def is_panel_affected(panel, hotspots, tracker):
        x, y, w, h = cv2.boundingRect(tracker)
        test_panel = np.array([((pt[0][0] + x), (pt[0][1] + y)) for pt in panel])
        offsets = [(0, 0), (5, 0), (5, 0), (0, 3), (0, 3)]
        for hotspot_idx, hotspot in enumerate(hotspots):
            # Check if hotspot has already been used
            if hotspot_idx in used_hotspots:
                continue
            M = cv2.moments(hotspot)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                for dx, dy in offsets:
                    if cv2.pointPolygonTest(test_panel, (cx + dx, cy + dy), False) >= 0:
                        used_hotspots.add(hotspot_idx)  # Add this hotspot to the used set
                        return True
        return False

    for idx, tracker in enumerate(trackers):
        x, y, w, h = cv2.boundingRect(tracker)
        tracker_roi = blue_mask[y:y+h, x:x+w]
        inverted_tracker_roi = cv2.bitwise_not(tracker_roi)
        panels = detect_contours(inverted_tracker_roi)
        panels = sorted(panels, key=lambda c: cv2.boundingRect(c)[1])
        for panel_jdx, panel in enumerate(panels):
            panel_geo_contour = _convert_to_geo_coordinates(panel, x, y)
            label = f"{idx+1}-{panel_jdx+1}"
            if is_panel_affected(panel, hotspots, tracker):
                center_x = sum(pt[0] for pt in panel_geo_contour) / len(panel_geo_contour)
                center_y = sum(pt[1] for pt in panel_geo_contour) / len(panel_geo_contour)
                affected_panels_coordinate[label] = (center_x, center_y)

    return affected_panels_coordinate






