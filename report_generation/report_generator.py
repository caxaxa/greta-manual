import pylatex as pl
from pylatex.utils import NoEscape, bold
from datetime import datetime
import json


def generate_report(df, area_name, stats_file):
    #build grouped df

    # Group the DataFrame by 'Nome das Imagens' and aggregate 'Painel' and 'Coordenadas Geográficas'
    grouped_df = df.groupby('Nome das Imagens').agg({
        'Painel': ', '.join,
        'Coordenadas Geográficas': 'first',
        'Facing North': 'first'
    }).reset_index()

    # Sorting by 'Painel'
    grouped_df = grouped_df.sort_values(by='Painel')

    # Get the current directory of the script
    # Get the current date
    current_date = datetime.now()

    author_dict = {"Lucas Chacha": "Técnico de IA"}

    area_name = area_name.replace("_", "\\_")

    # Paths

    orthophoto_path_img = ('report_images/ortho.png')
    aisol_logo_path = ('report_images/aisol_logo.png' )
    aisol_logo_2_path = ('report_images/logo_2.png' )
    layer_img_path = ('report_images/layer_img.png' )
    top_view =  ("report_images/topview.png")
    match =  ("report_images/matchgraph.png")
    overlap =  ("report_images/overlap.png")
    residual =  ("report_images/residual_histogram.png")
    with open(stats_file, "r") as file:
        stats = json.load(file)

    #Maint Text
    
    client_data = "Client data here..."


    abstract = "Thermography has emerged as an invaluable tool for the assessment of solar installations, especially in pinpointing operational inefficiencies manifested as 'hotspots'. This report encapsulates a detailed examination of such hotspots on solar panels and trackers. Initially, foundational data is provided in the form of client-specific identifiers and equipment specifics. A visual representation offers both an orthophoto, derived from the entirety of captured images, and a schematic map underscoring the locations of trackers and identified hotspots. Enumeration of these components is systematically organized from west to east and north to south for clarity. The precise locations and images used to discern these thermal anomalies are meticulously detailed in subsequent sections, providing stakeholders with a holistic and structured understanding of the solar installation's thermographic health."

    intro_text_pt = '''Thermography, leveraging infrared technology, is a pivotal tool for identifying thermal discrepancies in solar installations. This report employs advanced thermographic methodologies to discern and localize 'hotspots' on solar panels and trackers. Such hotspots, regions of elevated temperature, often indicate operational anomalies or material inefficiencies within the infrastructure.
    The report's first section, Client Data, presents a dataset that includes client-specific identifiers and equipment specifications. This encompasses details like solar panel model numbers, tracker serial numbers, installation dates, and previous maintenance logs. This data sets the foundation for a targeted analysis, aligning the thermographic outputs with the unique attributes of each solar component.
    Subsequently, the Visual Overview of the Area offers a spatial representation of the installation site. Utilizing geospatial coordinates, this section provides a scaled layout of the solar panels and trackers, establishing a reference matrix. The matrix aids in correlating thermographic findings with their exact geographic locations on the site, ensuring accurate hotspot localization.
    The final segment delves into the Drona Flight and Orthomosaic Image Construction. This section documents the drone's flight parameters including altitude, speed, and trajectory. The type of infrared sensors, their resolution, and sensitivity range are specified. The process of orthomosaic image synthesis is also detailed here, highlighting the algorithms employed for stitching together individual thermal captures into a unified thermal map of the entire installation.
    With this structured approach, the report aims to furnish a precise and technical analysis of the detected hotspots, facilitating actionable insights for targeted maintenance and system optimization.
    '''



    text_3_1_pt = ''' In this section, we present a comprehensive overview of the inspected area. Figure 1 displays the orthophoto, assembled from all captured images of the region. Concurrently, Figure 2 provides a schematic representation of the area, emphasizing the locations of the trackers and the detected hotspots. It also pinpoints each solar panel affected by these hotspots. The enumeration for trackers follows a specific pattern: from left to right (west to east) and from top to bottom (north to south). As such, the top-leftmost tracker is labeled as tracker number 1, with the adjacent panel also designated as number 1. Panel numbering increases progressively towards the south, while tracker numbering increments towards the east. '''
    
    if len(df)>0 :
        text_4_1_pt = ' This inspection identified hotspots impacting {} panels. The specific locations, along with the images utilized to detect these anomalies, are detailed in the subsequent section.'.format(str(len(df)))
    else:
        text_4_1_pt = ' No hotspots were detected in this area.'


    doc = pl.Document(documentclass="article", document_options='dvipsnames')



    # Add packages to preamble
    doc.preamble.append(pl.Command('usepackage', options='utf8', arguments='inputenc'))
    doc.packages.append(pl.Package('fancyhdr'))
    doc.packages.append(pl.Package('calc'))
    doc.packages.append(pl.Package('geometry'))
    doc.packages.append(pl.Package("graphicx"))
    doc.packages.append(pl.Package('placeins'))
    doc.packages.append(pl.Package('tikz'))
    doc.packages.append(pl.Package('xcolor'))


    # Adjust header and footer margins
    doc.preamble.append(NoEscape(r'\setlength{\headsep}{3cm}'))  # Adjust the value as needed
    doc.preamble.append(NoEscape(r'\setlength{\footskip}{1cm}'))  # Adjust the value as needed
    doc.preamble.append(NoEscape(r'\geometry{top=4cm}'))  # Adjust the 3cm value as needed
    # Configure the fancy header/footer settings
    # Adjust the size of the logo in the header
    doc.preamble.append(NoEscape(r'\fancyhead[L]{{\includegraphics[width=0.1\paperwidth]{{{}}}}}'.format(aisol_logo_2_path)))
    doc.preamble.append(NoEscape(r'\fancyhead[R]{Thermographic Report}'))
    doc.preamble.append(NoEscape(r'\fancyfoot[C]{GreTA® System, Beta Version - 2023         Powered by Aisol ®}'))
    doc.preamble.append(NoEscape(r'\usetikzlibrary{calc}'))


    #title_page_content 
    tikz_code = r"""
    \thispagestyle{empty}%

    \begin{tikzpicture}[overlay,remember picture]

    % Rectangles
    \shade[
    left color=lightgray, 
    right color=NavyBlue!40,
    transform canvas ={rotate around ={45:($(current page.north west)+(0,-6)$)}}] 
    ($(current page.north west)+(0,-6)$) rectangle ++(9,1.5);

    \shade[
    left color=lightgray,
    right color=lightgray!50,
    rounded corners=0.75cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(.5,-10)$)}}]
    ($(current page.north west)+(0.5,-10)$) rectangle ++(15,1.5);

    \shade[
    left color=lightgray,
    rounded corners=0.3cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(.5,-10)$)}}] ($(current page.north west)+(1.5,-9.55)$) rectangle ++(7,.6);

    \shade[
    left color=lightgray!80,
    right color=blue!60,
    rounded corners=0.4cm,
    transform canvas ={rotate around ={45:($(current page.north)+(-1.5,-3)$)}}]
    ($(current page.north)+(-1.5,-3)$) rectangle ++(9,0.8);

    \shade[
    left color=RoyalBlue!80,
    right color=blue!80,
    rounded corners=0.9cm,
    transform canvas ={rotate around ={45:($(current page.north)+(-3,-8)$)}}] ($(current page.north)+(-3,-8)$) rectangle ++(15,1.8);

    \shade[
    left color=lightgray,
    right color=RoyalBlue,
    rounded corners=0.9cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(4,-15.5)$)}}]
    ($(current page.north west)+(4,-15.5)$) rectangle ++(30,1.8);

    \shade[
    left color=RoyalBlue,
    right color=Emerald,
    rounded corners=0.75cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(13,-10)$)}}]
    ($(current page.north west)+(13,-10)$) rectangle ++(15,1.5);

    \shade[
    left color=lightgray,
    rounded corners=0.3cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(18,-8)$)}}]
    ($(current page.north west)+(18,-8)$) rectangle ++(15,0.6);

    \shade[
    left color=lightgray,
    rounded corners=0.4cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(19,-5.65)$)}}]
    ($(current page.north west)+(19,-5.65)$) rectangle ++(15,0.8);

    \shade[
    left color=RoyalBlue,
    right color=red!80,
    rounded corners=0.6cm,
    transform canvas ={rotate around ={45:($(current page.north west)+(20,-9)$)}}] 
    ($(current page.north west)+(20,-9)$) rectangle ++(14,1.2);

    % Year
    \draw[ultra thick,gray]
    ($(current page.center)+(5,2)$) -- ++(0,-3cm) 
    node[
    midway,
    left=0.25cm,
    text width=5cm,
    align=right,
    black!75
    ]
    {
    {\fontsize{25}{30} \selectfont \bf Área \\[10pt] 1}
    } 
    node[
    midway,
    right=0.25cm,
    text width=6cm,
    align=left,
    RoyalBlue]
    {
    {\fontsize{72}{86.4} \selectfont 2023}
    };

    % Title
    \node[align=center] at ($(current page.center)+(0,-5)$) 
    {
    {\fontsize{60}{72} \selectfont {{Thermographic Report}}} \\[1cm]
    {\fontsize{16}{19.2} \selectfont \textcolor{RoyalBlue}{ \bf Area Report}}\\[3pt]
    Greta System\\[3pt]
    Powered by:};
    \node[align=center] at ($(current page.center)+(0,-8)$) 
    {\includegraphics[width=0.1\paperwidth]{report_images/logo_2.png}'
    };
    \end{tikzpicture}
    """
    doc.append(NoEscape(tikz_code))

    # Verso Page
    doc.append(NoEscape(r'\newpage'))


    # Top part with logo and document name
    doc.append(NoEscape(r'\thispagestyle{empty}'))  # No headers or footers on this page

    # Spacer
    doc.append(NoEscape(r'\vspace*{0.4cm}'))

    # Line separator
    doc.append(NoEscape(r'\rule{\linewidth}{0.5pt}'))

    # Report's details centered
    doc.append(NoEscape(r'\thispagestyle{empty}'))  # No headers or footers on this page
    doc.append(NoEscape(r'\begin{center}'))
    doc.append(NoEscape(r'{\large\bfseries Thermal Imaging Inspection Report}'))
    doc.append(NoEscape(r'\vspace*{0.5cm}'))
    doc.append(NoEscape(r'\textbf{Responsável Técnico:} Fábio Corpa, Engineer'))
    doc.append(NoEscape(r'\textbf{CREA:} 12345678'))
    doc.append(NoEscape(r'\textbf{{Date:}} {{{}}}'.format(current_date.strftime("%B %Y"))))
    doc.append(NoEscape(r'\textbf{Localização:} Campo Grande, MS. Brasil'))
    doc.append(NoEscape(r'\textbf{Endereço:} Rua Manoel Inácio de Souza, n. 24, C.E.P : 79.020-220'))
    doc.append(NoEscape(r'\textbf{Software:} GreTA® - Georeferenced Thermographic Analysis System, Beta Version'))
    doc.append(NoEscape(r'\textbf{Versão:} Client Version'))
    doc.append(NoEscape(r'\end{center}'))

    # Spacer
    doc.append(NoEscape(r'\vspace*{0.4cm}'))

    # Line separator
    doc.append(NoEscape(r'\rule{\linewidth}{0.5pt}'))

    # Bottom part with copyrights
    doc.append(NoEscape(r'\vfill'))
    doc.append(NoEscape(r'\noindent\textbf{Copyright © 2023 Aisol Solucoes em Inteligência Artificial}'))
    doc.append(NoEscape(r'All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, without the prior written permission of the client.'))
    doc.append(NoEscape(r'\vspace*{0.2cm}'))
    doc.append(NoEscape(r'\noindent\textbf{ISBN:} xxxxxxxx'))


    # Other relevant data
    doc.append(bold("Location:"))
    doc.append("Campo Grande, MS. Brasil")
    doc.append("Rua Manoel Inácio de Souza, n. 24")
    doc.append("C.E.P : 79.020-220")
    doc.append(bold("Copyrights:"))
    doc.append("Aisol, 2023.")
    doc.append(bold("Release:"))
    doc.append("Client Version")
    doc.append(bold("Company:"))
    doc.append("Aisol Solucoes em Inteligência Artificial")

    # Abstract
    doc.append(NoEscape(r'\newpage'))
    doc.append(NoEscape(r'\begin{abstract}'))
    doc.append(NoEscape(abstract))
    doc.append(NoEscape(r'\end{abstract}'))

    doc.append(NoEscape(r'\pagestyle{fancy}'))

    # Table of contents, figures, and tables
    doc.append(NoEscape(r'\tableofcontents'))
    #doc.append(NoEscape(r'\listoffigures'))
    doc.append(NoEscape(r'\listoftables'))




    # Main Content
    doc.append(NoEscape(r'\section{Introduction}'))
    doc.append(intro_text_pt)
    doc.append(NoEscape(r'\section{Client Data}'))
    doc.append(client_data)
    doc.append(NoEscape(r'\section{%s}' % area_name))
    doc.append(text_3_1_pt)
    doc.append(NoEscape(r'\FloatBarrier'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(orthophoto_path_img)
        fig.add_caption("Orthophoto")
    doc.append(NoEscape(r'\FloatBarrier'))

    # Table
    if not df.empty:
        # Split DataFrame into chunks of 15 rows
        chunks = [df[['Painel','Coordenadas Geográficas']].iloc[i:i+45] for i in range(0, len(df), 45)]
        
        for chunk in chunks:
              # Start centering
            with doc.create(pl.Table(position='h!')) as table:
                # Convert DataFrame chunk to Tabular format
                tabular = pl.Tabular('l' * len(chunk.columns))
                tabular.add_hline()
                tabular.add_row(chunk.columns)
                tabular.add_hline()
                for index, row in chunk.iterrows():
                    tabular.add_row(row)
                    tabular.add_hline()
                doc.append(NoEscape(r'\FloatBarrier'))
                doc.append(NoEscape(r'\begin{center}'))
                table.append(tabular)
                doc.append(NoEscape(r'\end{center}'))
                doc.append(NoEscape(r'\FloatBarrier'))
                table.add_caption("Table of Affected Solar Panels")
              # End centering
        doc.append(NoEscape(r'\FloatBarrier'))
        with doc.create(pl.Figure(position='h!')) as fig:
            fig.add_image(layer_img_path)
            fig.add_caption("Enumerated Affected Panels")
        doc.append(NoEscape(r'\FloatBarrier'))
        doc.append(NoEscape(r'\newpage'))      
        doc.append(NoEscape(r'\section{Main Findings}'))
        doc.append(text_4_1_pt)
        # Iterate through grouped_df and add sections for each unique image
        for _, row in grouped_df.iterrows():
            with doc.create(pl.Section(row['Painel'])):
                doc.append(NoEscape(r'\begin{figure}[h!]'))
                doc.append(NoEscape(r'\centering'))
                if row['Facing North']:
                    doc.append(NoEscape(r'''
                        \begin{minipage}{0.29\linewidth}
                            \includegraphics[width=\linewidth]{report_images/''' + row['Nome das Imagens'].replace('_MASKED', '_MAP') + r'''}
                        \end{minipage}%
                        \hfill
                        \begin{minipage}{0.31\linewidth}
                            \includegraphics[width=\linewidth]{report_images/''' + row['Nome das Imagens'].replace('_MASKED', '_T') + r'''}
                        \end{minipage}%
                        \hfill
                        \begin{minipage}{0.31\linewidth}
                            \includegraphics[width=\linewidth]{report_images/''' + row['Nome das Imagens'] + r'''}
                        \end{minipage}
                    '''))
                else:
                    doc.append(NoEscape(r'''
                        \begin{minipage}{0.29\linewidth}
                            \includegraphics[width=\linewidth]{report_images/''' + row['Nome das Imagens'].replace('_MASKED', '_MAP') + r'''}
                        \end{minipage}%
                        \hfill
                        \begin{minipage}{0.31\linewidth}
                            \includegraphics[width=\linewidth, angle=180]{report_images/''' + row['Nome das Imagens'].replace('_MASKED', '_T') + r'''}
                        \end{minipage}%
                        \hfill
                        \begin{minipage}{0.31\linewidth}
                            \includegraphics[width=\linewidth, angle=180]{report_images/''' + row['Nome das Imagens'] + r'''}
                        \end{minipage}
                    '''))
                doc.append(NoEscape(r'\caption{' + 'Image: ' + str(row['Nome das Imagens']).replace("_", "\\_") + '}'))
                doc.append(NoEscape(r'\label{fig:my_label}'))
                doc.append(NoEscape(r'\end{figure}'))
                doc.append(NoEscape(r'\FloatBarrier'))
                doc.append(NoEscape(r'The image name for inspection is ' + str(row['Nome das Imagens']).replace("_", "\\_") +  ' .'))
                doc.append(NoEscape(r'The affected panels in this Image are ' + row['Painel']) + ' . ' )
    else:
        doc.append("No affected panels were found.")
        return doc.dumps()
    


    def create_processing_stats_table(stats):
        processing_stats = stats['processing_statistics']
        data = [
            ['Feature Extraction', processing_stats['steps_times']['Feature Extraction']],
            ['Features Matching', processing_stats['steps_times']['Features Matching']],
            ['Tracks Merging', processing_stats['steps_times']['Tracks Merging']],
            ['Reconstruction', processing_stats['steps_times']['Reconstruction']],
            ['Total Time', processing_stats['steps_times']['Total Time']]
        ]
        table = pl.Tabular('lr')
        table.add_hline()
        for row in data:
            table.add_row(row)
            table.add_hline()
        with doc.create(pl.Center()) as centered:
            with centered.create(pl.Table(position='h!')) as table_with_caption:
                table_with_caption.add_caption("Processing Statistics")
                table_with_caption.append(NoEscape(r'\begin{center}'))
                table_with_caption.append(table)
                table_with_caption.append(NoEscape(r'\end{center}'))
        return centered  # returning the centered environment containing the table

    def create_features_stats_table(stats):
        features_stats = stats['features_statistics']
        detected_features = features_stats['detected_features']
        reconstructed_features = features_stats['reconstructed_features']
        data = [
            ['Detected Features - Min', detected_features['min']],
            ['Detected Features - Max', detected_features['max']],
            ['Detected Features - Mean', detected_features['mean']],
            ['Detected Features - Median', detected_features['median']],
            ['Reconstructed Features - Min', reconstructed_features['min']],
            ['Reconstructed Features - Max', reconstructed_features['max']],
            ['Reconstructed Features - Mean', reconstructed_features['mean']],
            ['Reconstructed Features - Median', reconstructed_features['median']]
        ]
        table = pl.Tabular('lr')
        table.add_hline()
        for row in data:
            table.add_row(row)
            table.add_hline()
        with doc.create(pl.Center()) as centered:
            with centered.create(pl.Table(position='h!')) as table_with_caption:
                table_with_caption.add_caption("Feature Statistics")
                table_with_caption.append(NoEscape(r'\begin{center}'))
                table_with_caption.append(table)
                table_with_caption.append(NoEscape(r'\end{center}'))
        return centered  # returning the centered environment containing the table

    def create_reconstruction_stats_table(stats):
        reconstruction_stats = stats['reconstruction_statistics']
        data = [
            ['Components', reconstruction_stats['components']],
            ['Has GPS', reconstruction_stats['has_gps']],
            ['Initial Points Count', reconstruction_stats['initial_points_count']],
            ['Reconstructed Points Count', reconstruction_stats['reconstructed_points_count']]
            # ... You can add more fields as necessary
        ]
        table = pl.Tabular('lr')
        table.add_hline()
        for row in data:
            table.add_row(row)
            table.add_hline()
        with doc.create(pl.Center()) as centered:
            with centered.create(pl.Table(position='h!')) as table_with_caption:
                table_with_caption.add_caption("Reconstruction Statistics")
                table_with_caption.append(NoEscape(r'\begin{center}'))
                table_with_caption.append(table)
                table_with_caption.append(NoEscape(r'\end{center}'))
        return centered  # returning the centered environment containing the table

    def create_camera_errors_table(stats):
        camera_errors = stats['camera_errors']
        camera_key = next(iter(camera_errors))  # Assuming one camera type in the example
        initial_values = camera_errors[camera_key]['initial_values']
        optimized_values = camera_errors[camera_key]['optimized_values']
        data = [
            ['Initial k1', initial_values['focal']],
            ['Optimized k1', optimized_values['focal']]
            # ... You can add more fields for initial and optimized values as necessary
        ]
        table = pl.Tabular('lr')
        table.add_hline()
        for row in data:
            table.add_row(row)
            table.add_hline()
        with doc.create(pl.Center()) as centered:
            with centered.create(pl.Table(position='h!')) as table_with_caption:
                table_with_caption.add_caption("Camera Errors")
                table_with_caption.append(NoEscape(r'\begin{center}'))
                table_with_caption.append(table)
                table_with_caption.append(NoEscape(r'\end{center}'))
        return centered  # returning the centered environment containing the table

    def create_gps_errors_table(stats):
        gps_errors = stats['gps_errors']

        # Construct the data list for the table
        data = [
            ['Mean X', gps_errors['mean']['x']],
            ['Mean Y', gps_errors['mean']['y']],
            ['Mean Z', gps_errors['mean']['z']],
            ['STD X', gps_errors['std']['x']],
            ['STD Y', gps_errors['std']['y']],
            ['STD Z', gps_errors['std']['z']],
            ['Error X', gps_errors['error']['x']],
            ['Error Y', gps_errors['error']['y']],
            ['Error Z', gps_errors['error']['z']],
            ['Average Error', gps_errors['average_error']],
            ['CE90', gps_errors['ce90']],
            ['LE90', gps_errors['le90']]
        ]

        # Create the table with the data
        table = pl.Tabular('lr')
        table.add_hline()
        for row in data:
            table.add_row(row)
            table.add_hline()

        # Center the table and add a caption
        with doc.create(pl.Center()) as centered:
            with centered.create(pl.Table(position='h!')) as table_with_caption:
                table_with_caption.add_caption("GPS Errors")
                table_with_caption.append(NoEscape(r'\begin{center}'))
                table_with_caption.append(table)
                table_with_caption.append(NoEscape(r'\end{center}'))

        return centered  # returning the centered environment containing the table

    doc.append(NoEscape(r'\newpage'))
    doc.append(NoEscape(r'\appendix'))
    doc.append(NoEscape(r'\section{Drone and Flight Information}'))
    doc.append(NoEscape(r'\newcommand{\rotatedimage}[1]{\includegraphics[angle=90, width=0.8\textwidth]{#1}}'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.append(NoEscape(r'\rotatedimage{' + top_view + '}'))
    doc.append("Drone Flight Information.")
    create_processing_stats_table(stats)

    # Orthophoto Data (to be created)
    doc.append(NoEscape(r'\section{Orthophoto Data}'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(match)
        fig.add_caption("Match Graph")
    doc.append("Descricao do gafico.")
    #create_camera_errors_table(stats)
    create_gps_errors_table(stats)

    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(overlap)
        fig.add_caption("Overlap Graph")
    doc.append("Descricao do gafico.")
    create_reconstruction_stats_table(stats)

    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(residual)
        fig.add_caption("Model Residual")
    doc.append("Descricao do gafico.")
    create_features_stats_table(stats)

    return doc.dumps()


