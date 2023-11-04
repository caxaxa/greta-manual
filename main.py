from image_processing.processing import create_masks_from_orthophoto, generate_affected_panels_coordinates
from image_processing.image_creation import save_image_with_masks_and_numbers, create_maps
from helpers.helpers import load_orthophoto
from report_generation.report_generator import generate_report
from report_generation.df_generator import create_df, save_xls
from report_generation.tex_to_pdf import run_pdflatex
from report_generation.preparing_images import locate_images_with_affected_panels, copy_images 
from DXF_layers.layer_generator import process_geotiff
from DXF_layers.dxf_processing import dxf_file_path
import os


if __name__ == "__main__":
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    #get farea name from user DB
    area_name = 'Area 1'

    # Construct the relative path
    ortho_path = os.path.join(current_dir, "Inputs", "odm_orthophoto", "odm_orthophoto.tif")
    print('Loading Ortophoto')
    ortho_img = load_orthophoto(ortho_path)

    # Path for the dxf directory
    print('Searching for .dfx file')
    dxf_file_path = dxf_file_path(current_dir)

    # Create the masks
    print('Creating Masks')
    blue_mask, red_mask = create_masks_from_orthophoto(ortho_img, debug = True)
    print('Masks  created')
    # Locate the mask for running the report

    affected_panels_coord = generate_affected_panels_coordinates(ortho_path, blue_mask, red_mask)
    print('Map of affected panels created')

    #Create and Copy images to report folder
    # Create the Layer Image:
    print('Creating Map Image')
    layer_image_path = os.path.join(current_dir, "report", "report_images", "layer_img.png")

    white_img = save_image_with_masks_and_numbers(blue_mask, red_mask, affected_panels_coord, ortho_path, layer_image_path, debug =  False)

    print('Layer image successfully generated')


    # Building the Report

    # Prepare the dataframe with georeferenced images for the report:

    df = create_df(affected_panels_coord)

    print('Dataframe successfully prepared')

    #Preparing Images for the Report:
    updated_df = locate_images_with_affected_panels(df,current_dir)

    print('Drawing Maps')

    # Ensure the 'report' directory exists
    report_dir = os.path.join(current_dir, "report")
    # Generating Latex Report:

    create_maps(ortho_path, white_img, updated_df, report_dir)

    print('Copying Images to Input Folders')

    copy_images(updated_df)

    

    print('Images successfully prepared')

    stats_file = os.path.join(report_dir,  'report_images' ,'stats.json')

    latex_code = generate_report(updated_df , area_name, stats_file)

    latex_report_path = os.path.join(report_dir, "report.tex")

    with open(latex_report_path, "w", encoding='utf-8') as f:
        f.write(latex_code)

    # Compile the .tex file
    run_pdflatex("report.tex", report_dir)

    print('First Compilation Successful')

    # Compile second time... Latex may need extra compilation to run packeges and references properly
    run_pdflatex("report.tex", report_dir)

    print('Second Compilation Successful')

    print('PDF report successfully generated')

    #Generate DFX Layers for the area

    print('Saving Dataframe in XLS')

    xlsx_path = os.path.join(current_dir, 'Output' , f'{area_name}.xlsx')

    save_xls(df, xlsx_path)

    print('XLS Successfully Created')

    if dxf_file_path:
        print('Creating DXF Layers')
        # Instantiate the GeoImageProcessor with paths to the GeoTIFF and DXF files.
        process_geotiff(ortho_path, dxf_file_path,blue_mask, red_mask,area_name)
        print('DXF layers successfully generated')
    else: print('No DXF Available')

    print('GRETA Finished Successfully!')