#from image_processing.processing import  json_to_contours_by_label, get_defect_centroids
from image_processing.image_creation import generate_defect_map, annotate_and_downscale_orthophoto
from helpers.helpers import load_orthophoto
from report_builder.report_generator import generate_report
from report_builder.tex_to_pdf import run_pdflatex
from report_builder.preparing_images import process_and_rename_images, annotate_and_crop_defect_area
from DXF_layers.layer_generator import process_geotiff
from DXF_layers.dxf_processing import dxf_file_path
import os
import json

if __name__ == "__main__":
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    #get farea name from user DB
    area_name = 'Area 1'

    # Construct the relative path
    ortho_path = os.path.join(current_dir, "Inputs", "manual_labeling", "map_cropped.tif")
    print('Loading Ortophoto')
    ortho_img = load_orthophoto(ortho_path)

    # Path for the dxf directory
    print('Searching for .dfx file')
    dxf_file_path = dxf_file_path(current_dir)

    # Create Annotation Counturns
    json_path = os.path.join(current_dir, "Inputs", "manual_labeling", "labels_cropped.json")

    report_dir = os.path.join(current_dir,'output', "report", "")

    report_images_dir = os.path.join(current_dir, report_dir, "report_images", "")

    new_ortho_path = os.path.join(current_dir, report_images_dir, "ortho.png")

    print('Annotating and Downscaling Ortophoto')
    # Load JSON data
    annotate_and_downscale_orthophoto(
        ortho_path = ortho_path, 
        json_path = json_path, 
        output_path = new_ortho_path, 
        scale_factor=0.25
    )

    # Create a dictionary, with the counting and the labels
    contours_by_label = json_to_contours_by_label(json_path)


    defect_centroids = get_defect_centroids(
        tif_path = ortho_path,
        contours_by_label = contours_by_label,  # Assuming it's already generated
        output_json="defect_centroids.json"
    )
    print('Defected Panels Located')

    print('Creating Map Image')
    


    layer_image_path = os.path.join(current_dir, report_images_dir, "layer_img.png")


                                    
    # Creating a deffects dict
    defects_dict = generate_defect_map(
        tif_path= ortho_path,
        contours_by_label=contours_by_label,  # existing contours
        alignment='vertical',  # or 'horizontal'
        output_image= layer_image_path
    )                              
    print('Layer image successfully generated')

    print('Annotating the Original Orthophoto')

    # Building the Report

    print('Processing Renaming and Moving Images')


    raw_images_dir = os.path.join(current_dir, "Inputs", "raw_images","")


    process_and_rename_images(
        raw_images_dir = raw_images_dir,
        output_dir = report_images_dir,
        defects_dict = defects_dict,
        alignment='vertical'
    )

    print('Crop the map Images')


    annotate_and_crop_defect_area(
        tif_path = ortho_path,
        defects_dict = defects_dict,
        contours_by_label = contours_by_label, 
        layer_image_path = layer_image_path,
        default_panel_width=127,
        crop_panel_size=5,
        output_dir= report_images_dir
    )


    # Generating Latex Report:

    print('Images successfully prepared')

    #stats_file = os.path.join(report_dir,  'report_images' ,'stats.json')

    latex_code = generate_report(defects_dict, defect_centroids, 'Área Teste', current_dir)

    latex_report_path = os.path.join(current_dir, report_dir, "report.tex")

    with open(latex_report_path, "w", encoding='utf-8') as f:
        f.write(latex_code)

    print('Report Latex File Created')

    #Compile the .tex file
    run_pdflatex("report.tex", report_dir)

    print('First Compilation Successful')

    # Compile second time... Latex may need extra compilation to run packeges and references properly
    run_pdflatex("report.tex", report_dir)

    print('Second Compilation Successful')

    print('PDF report successfully generated')

    # #Generate DFX Layers for the area

    # print('Saving Dataframe in XLS')

    # xlsx_path = os.path.join(current_dir, 'Output' , f'{area_name}.xlsx')

    # save_xls(df, xlsx_path)

    # print('XLS Successfully Created')

    # if dxf_file_path:
    #     print('Creating DXF Layers')
    #     # Instantiate the GeoImageProcessor with paths to the GeoTIFF and DXF files.
    #     process_geotiff(ortho_path, dxf_file_path,blue_mask, red_mask,area_name)
    #     print('DXF layers successfully generated')
    # else: print('No DXF Available')

    # print('GRETA Finished Successfully!')