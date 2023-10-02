from image_processing.processing import create_masks_from_orthophoto, generate_affected_panels_coordinates
from image_processing.image_creation import save_image_with_masks_and_numbers
from helpers.helpers import load_orthophoto, display_image
from report_generation.report_generator import generate_report
from report_generation.df_generator import dict_to_dataframe, transform_coordinates
from report_generation.tex_to_pdf import run_pdflatex
from report_generation.preparing_images import locate_images_with_affected_panels, copy_images 
from DXF_layers.layer_generator import GeoImageProcessor, detect_contours, BLACK_COLOR, RED_COLOR
from DXF_layers.dxf_processing import dxf_file_path
import subprocess
import cv2
import os

if __name__ == "__main__":
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the relative path
    ortho_path = os.path.join(current_dir, "Inputs", "odm_orthophoto", "odm_orthophoto.tif")
    ortho_img = load_orthophoto(ortho_path)

    # Path for the dxf directory
    
    dxf_file_path = dxf_file_path(current_dir)

    # Create the masks
    blue_mask, red_mask = create_masks_from_orthophoto(ortho_img)
    print('Masks  created')
    # Locate the mask for running the report

    affected_panels_coord = generate_affected_panels_coordinates(ortho_path, blue_mask, red_mask)
    print('Affected Panel  created')

    #Create and Copy images to report folder
    # Create the Layer Image:
    layer_image_path = os.path.join(current_dir, "report", "report_images", "layer_img.png")

    save_image_with_masks_and_numbers(blue_mask, red_mask, affected_panels_coord, ortho_path, layer_image_path)

    print('Layer image successfully generated')

    # Building the Report

    # Prepare the dataframe with georeferenced images for the report:

    df = dict_to_dataframe(affected_panels_coord)

    df_transformed = transform_coordinates(df)

    df = df_transformed

    print('Dataframe successfully prepared')

    #Preparing Images for the Report:
    updated_df = locate_images_with_affected_panels(df)
    copy_images(updated_df)

    print('Images successfully prepared')

    # Ensure the 'report' directory exists
    report_dir = os.path.join(current_dir, "report")

    # Generating Latex Report:
    latex_code = generate_report(df)

    latex_report_path = os.path.join(report_dir, "report.tex")
    latex_report_path_debug = os.path.join(report_dir, "report_debug.txt")

    with open(latex_report_path_debug, "w") as f:
        f.write(latex_code)
    print('Latex report successfully generated')


    with open(latex_report_path, "w") as f:
        f.write(latex_code)
    print('Latex report successfully generated')

    # # Compile the .tex file
    # run_pdflatex("report.tex", report_dir)

    print('PDF report successfully generated')

    #Generate DFX Layers for the area

    if dxf_file_path:
        # Instantiate the GeoImageProcessor with paths to the GeoTIFF and DXF files.


        processor = GeoImageProcessor(ortho_path, dxf_file_path)

        # Detect the solar panel trackers from the blue mask (new_mask).
        trackers = detect_contours(blue_mask)
        trackers = sorted(trackers, key=lambda c: cv2.boundingRect(c)[0])

        # Detect the hotspots from the red mask (red_mask).
        hotspots = detect_contours(red_mask)
        hotspots = sorted(hotspots, key=lambda c: cv2.boundingRect(c)[0])
        # Draw and fill the detected hotspot contours on the DXF.
        for hotspot in hotspots:
            processor.draw_and_fill_contour(hotspot, 'GRETA - Hotspots', RED_COLOR)

        # will be shown in a new mask called 'GRETA - Trackers Afetados'.
        for idx, tracker in enumerate(trackers):
            processor.draw_contour(tracker, 'GRETA - Máscara dos Trackers')
            processor.detect_and_annotate_panels(tracker, idx, blue_mask, hotspots)

        # Save the modified DXF file.
        processor.save(dxf_file_path)
    print('DXF layers successfully generated')