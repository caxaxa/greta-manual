import pylatex as pl
from pylatex.utils import NoEscape, bold
from datetime import datetime
import json
import os

def generate_report(defects_dict, defect_centroids, area_name, current_dir):
    """
    Generate a thermographic inspection report for solar power plants.
    The source code is in English, but the client report is in Portuguese.
    """
    # Format the area name for LaTeX and define paths
    area_name = area_name.replace("_", "\\_")
    report_images_dir = "report_images"
    orthophoto_path_img = os.path.join(report_images_dir, 'ortho.png')
    aisol_logo_path = os.path.join(report_images_dir, 'aisol_logo.png')
    aisol_logo_2_path = os.path.join(report_images_dir, 'logo_2.png')
    layer_img_path = os.path.join(report_images_dir, 'layer_img.png')
    top_view = os.path.join(report_images_dir, "topview.png")
    match = os.path.join(report_images_dir, "matchgraph.png")
    overlap = os.path.join(report_images_dir, "overlap.png")
    residual = os.path.join(report_images_dir, "residual_histogram.png")
    
    current_date = datetime.now()

    # Client and report texts
    client_data = "Anonimizado"
    abstract = ("As inspeções termográficas tornaram-se uma ferramenta essencial para avaliar o desempenho e a confiabilidade "
                "de usinas solares. Este estudo foca na detecção e análise de "
                "\\textbf{pontos quentes (hotspots), diodos de bypass queimados e painéis ou strings inativos}, "
                "indicadores críticos de ineficiências operacionais. \\textbf{Hotspots} aparecem como regiões de alta "
                "temperatura localizadas nos painéis solares, frequentemente causadas por sombreamento, acúmulo de sujeira ou "
                "células fotovoltaicas defeituosas, podendo levar à degradação do desempenho e danos a longo prazo. "
                "\\textbf{Diodos de bypass queimados} interrompem o fluxo elétrico esperado, causando o superaquecimento de fileiras "
                "inteiras de células (\\textbf{hot lines}), o que pode reduzir significativamente a eficiência do sistema. "
                "Além disso, \\textbf{painéis ou strings inativos} — identificados como regiões mais frias do que o esperado nas "
                "imagens térmicas — indicam possíveis falhas em inversores, desconexões ou problemas elétricos. "
                "A detecção precoce e a implementação de ações corretivas direcionadas podem otimizar a geração de energia, "
                "prolongar a vida útil do sistema e prevenir falhas onerosas.")
    
    intro_text_pt = ("A termografia, utilizando tecnologia infravermelha, é uma ferramenta fundamental para identificar discrepâncias "
                     "térmicas em instalações solares. Este relatório emprega metodologias termográficas avançadas para detectar e localizar "
                     "\\textbf{pontos quentes (hotspots)} em painéis solares e rastreadores. Esses hotspots, caracterizados por regiões de temperatura elevada, "
                     "geralmente indicam anomalias operacionais ou ineficiências materiais na infraestrutura. "
                     "\n\n"
                     "A primeira seção do relatório, \\textbf{Dados do Cliente}, apresenta um conjunto de dados que inclui identificadores específicos do cliente "
                     "e especificações dos equipamentos. Em seguida, a \\textbf{Visão Geral da Área} oferece uma representação espacial do local da instalação. "
                      "Utilizando coordenadas geoespaciais, esta seção fornece um layout escalado dos painéis solares e rastreadores, estabelecendo uma matriz de referência. "
                     "\n\n")

    drone_intro = ("A última seção aborda o \\textbf{Voo do Drone e a Construção da Imagem Ortorretificada}, onde são documentados os parâmetros do voo do drone, "
                     "incluindo altitude, velocidade e trajetória, além dos detalhes dos sensores infravermelhos empregados.")
    
    text_3_1_pt = (" Nesta seção, apresentamos uma visão abrangente da área inspecionada. A \\textbf{Figura 1} exibe a \\textbf{ortofoto} montada a partir de todas as imagens capturadas "
                   "da região. A \\textbf{Figura 2} apresenta uma representação esquemática da área, destacando as localizações dos rastreadores e dos hotspots detectados. "
                   "A numeração dos rastreadores segue o padrão: da esquerda para a direita (de oeste para leste) e de cima para baixo (de norte para sul).")

    # Load processing statistics if available
    stats_file = os.path.join(current_dir, 'Output', 'report', 'report_images', 'stats.json')
    stats = None
    if os.path.exists(stats_file):
        with open(stats_file, "r") as file:
            stats = json.load(file)

    # Document setup with additional academic packages
    doc = pl.Document(documentclass="article", document_options='dvipsnames')
    doc.preamble.append(pl.Command('usepackage', options='utf8', arguments='inputenc'))
    doc.preamble.append(pl.Command('usepackage', options='brazil', arguments='babel'))
    doc.packages.append(pl.Package('geometry'))
    doc.packages.append(pl.Package("graphicx"))
    doc.packages.append(pl.Package('placeins'))
    doc.packages.append(pl.Package('calc'))
    doc.packages.append(pl.Package('tikz'))
    doc.packages.append(pl.Package('xcolor'))
    doc.packages.append(pl.Package('fancyhdr'))
    # Add booktabs for a cleaner table layout
    doc.packages.append(pl.Package('booktabs'))

    # Adjust header and footer margins
    doc.preamble.append(NoEscape(r'\setlength{\headsep}{3cm}'))
    doc.preamble.append(NoEscape(r'\setlength{\footskip}{1cm}'))
    doc.preamble.append(NoEscape(r'\geometry{top=4cm}'))

    # Configure fancyhdr
    logo_path_fixed = aisol_logo_2_path.replace('\\', '/') # NECESSARY TO INVERT THE '/' IN LATEX
    doc.preamble.append(NoEscape(r'\fancyhead[L]{{\includegraphics[width=0.1\paperwidth]{{{}}}}}'.format(logo_path_fixed)))

    doc.preamble.append(NoEscape(r'\fancyhead[R]{Relatóriio Termográfico}'))
    doc.preamble.append(NoEscape(r'\fancyfoot[C]{GreTA®, Versão Beta - 2025 \quad Desenvolvido por Aisol}'))
    doc.preamble.append(NoEscape(r'\usetikzlibrary{calc}'))

    # Title page with TikZ content from external file
    tikz_template = os.path.join(current_dir, "report_builder", "tikz_code.txt")
    with open(tikz_template, "r", encoding="utf-8") as f:
        tikz_code = f.read()
    doc.append(NoEscape(tikz_code))
    doc.append(NoEscape(r'\newpage'))

    # Title & basic report details
    doc.append(NoEscape(r'\thispagestyle{empty}'))
    doc.append(NoEscape(r'\vspace*{0.4cm}'))
    doc.append(NoEscape(r'\rule{\linewidth}{0.5pt}'))
    doc.append(NoEscape(r'\begin{center}'))
    doc.append(NoEscape(r'{\large\bfseries Relatório de Inspeção por Imagem Térmica.  }'))
    doc.append(NoEscape(r'\vspace*{0.5cm}'))
    doc.append(NoEscape(r'\textbf{Responsável Técnico:} ANONIMIZADO, Engineer.  '))
    doc.append(NoEscape(r'\textbf{CREA:} 12345678  '))
    doc.append(NoEscape(r'\textbf{{Date:}} {}'.format(current_date.strftime("%B %Y"))))
    doc.append(NoEscape(r'\textbf{Localização:} Campo Grande, MS. Brasil.  '))
    doc.append(NoEscape(r'\textbf{Endereço:} Rua Manoel Inácio de Souza, n. 24, C.E.P : 79.020-220  '))
    doc.append(NoEscape(r'\textbf{Software:} GreTA® - Georeferenced Thermographic Analysis System, Versão Beta.  '))
    doc.append(NoEscape(r'\textbf{Versão:} Versão ANONIMIZADA  '))
    doc.append(NoEscape(r'\end{center}'))
    doc.append(NoEscape(r'\vspace*{0.4cm}'))
    doc.append(NoEscape(r'\rule{\linewidth}{0.5pt}'))
    doc.append(NoEscape(r'\vfill'))
    doc.append(NoEscape(r'\noindent\textbf{Copyright © 2025 Aisol Soluções em Inteligência Artificial.  }'))
    doc.append(NoEscape(r'Todos os direitos reservados. Nenhuma parte desta publicação pode ser reproduzida, distribuída ou transmitida sem autorização prévia.  '))
    doc.append(NoEscape(r'\vspace*{0.2cm}'))
    doc.append(NoEscape(r'\noindent\textbf{ISBN:} xxxxxxxx.  '))



    
    # Additional report data
    doc.append(bold("Location:"))
    doc.append("Campo Grande, MS. Brasil.  ")
    doc.append("Rua Manoel Inácio de Souza, n. 24.  ")
    doc.append("C.E.P : 79.020-220.  ")
    doc.append(bold("Copyrights:"))
    doc.append("Aisol, 2023.  ")
    doc.append(bold("Release:"))
    doc.append("VERSAO ANONIMIZADA.  ")
    doc.append(bold("Company:"))
    doc.append("Aisol Soluções em Inteligência Artificial em parceria com PVX Engenharia.  ")
    doc.append(NoEscape(r'\newpage'))
            
    # Table of contents
    doc.append(NoEscape(r'\tableofcontents'))
    doc.append(NoEscape(r'\newpage'))

    # Abstract page
    doc.append(NoEscape(r'\newpage'))
    doc.append(NoEscape(r'\begin{abstract}'))
    doc.append(NoEscape(abstract))
    doc.append(NoEscape(r'\end{abstract}'))
    doc.append(NoEscape(r'\pagestyle{fancy}'))

    # Main Content Sections
    doc.append(NoEscape(r'\section{Introduction}'))
    doc.append(intro_text_pt)
    if stats:
        doc.append(drone_intro)
    doc.append(NoEscape(r'\section{Dados do Cliente}'))
    doc.append(client_data)
    doc.append(NoEscape(r'\section{Visão Geral da Área}'))
    doc.append(text_3_1_pt)
    doc.append(NoEscape(r'\FloatBarrier'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(orthophoto_path_img)
        fig.add_caption("Ortofoto")
    doc.append(NoEscape(r'\FloatBarrier'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(layer_img_path)
        fig.add_caption("Máscara dos Painéis")
    doc.append(NoEscape(r'\FloatBarrier'))

    # --- Defect Summary Table in academic style ---
    if defects_dict:
        # Define maximum number of rows per table.
        rows_per_table = 35
        defects_items = list(defects_dict.items())
        total_rows = len(defects_items)
        
        for batch_idx in range(0, total_rows, rows_per_table):
            # Create a new table for each batch of rows.
            with doc.create(pl.Table(position='h!')) as table:
                # Use a continuation caption for subsequent tables.
                caption = ("Resumo dos Defeitos Identificados" 
                        if batch_idx == 0 
                        else "Resumo dos Defeitos Identificados (cont.)")
                table.add_caption(caption)
                with doc.create(pl.Tabular("lll")) as tabular:
                    tabular.append(NoEscape(r'\toprule'))
                    tabular.add_row(["Tipo de Problema", "Local do Painel", "Coordenadas"], escape=False)
                    tabular.append(NoEscape(r'\midrule'))
                    # Add rows for the current batch.
                    for label, defect in defects_items[batch_idx:batch_idx + rows_per_table]:
                        tabular.add_row([defect["issue_type"], label, str(defect["panel_centroid_geospatial"])])
                    tabular.append(NoEscape(r'\bottomrule'))
            # Insert a FloatBarrier to ensure tables are rendered in sequence.
            doc.append(NoEscape(r'\FloatBarrier'))
    else:
        doc.append("Nenhum defeito identificado.")


    # --- Defect Presentation by Issue Type ---
    # Define the expected defect types and their corresponding section titles in Portuguese.
    # Update expected_types to match the new mappings:
    expected_types = {
        "hotspots": "Pontos Quentes (Hot Spots)",
        "offlinepanels": "Painéis Desligados",
        "faultydiodes": "Diodos de Bypass Queimados"
    }

    # Group defects by their lowercase issue type if it is one of the expected keys.
    defects_by_type = {}
    for label, defect in defects_dict.items():
        issue = defect["issue_type"].lower()
        if issue in expected_types:
            defects_by_type.setdefault(issue, []).append((label, defect))

    # For each expected type, create a section with the corresponding title.
    for key, section_title in expected_types.items():
        doc.append(NoEscape(r'\newpage'))
        doc.append(NoEscape(r'\section{' + section_title + '}'))
        if key in defects_by_type and defects_by_type[key]:
            for label, defect in defects_by_type[key]:
                # Build image paths assuming the naming convention remains the same.
                defect_image = os.path.join(report_images_dir, f"{defect['issue_type']}_{label}_cropped.jpg")
                defect_map = os.path.join(report_images_dir, f"{defect['issue_type']}_{label}_map.jpg")
                drone_img = os.path.join(report_images_dir, f"{defect['issue_type']}_{label}.jpg")
                
                with doc.create(pl.Figure(position='h!')) as fig:
                    fig.append(NoEscape(r'\begin{minipage}{0.31\linewidth}'))
                    fig.append(NoEscape(r'\centering'))
                    fig.add_image(defect_map, width=NoEscape(r'\linewidth'))
                    fig.append(NoEscape(r'\caption{Localização do defeito: ' + label + '}'))
                    fig.append(NoEscape(r'\end{minipage}%'))
                    fig.append(NoEscape(r'\hfill'))
                    fig.append(NoEscape(r'\begin{minipage}{0.31\linewidth}'))
                    fig.append(NoEscape(r'\centering'))
                    fig.add_image(defect_image, width=NoEscape(r'\linewidth'))
                    fig.append(NoEscape(r'\caption{Zoom no defeito: ' + label + '}'))
                    fig.append(NoEscape(r'\end{minipage}%'))
                    fig.append(NoEscape(r'\hfill'))
                    fig.append(NoEscape(r'\begin{minipage}{0.31\linewidth}'))
                    fig.append(NoEscape(r'\centering'))
                    fig.add_image(drone_img, width=NoEscape(r'\linewidth'))
                    fig.append(NoEscape(r'\caption{Imagem Original: ' + label + '}'))
                    fig.append(NoEscape(r'\end{minipage}'))
                
                # Insert a FloatBarrier to ensure figures appear above the following text
                doc.append(NoEscape(r'\FloatBarrier'))
                
                # Descriptive text for each defect type
                if key == "hotspots":
                    doc.append(f"No painel {label} há sinais de pontos quentes conforme as figuras acima.\n")
                elif key == "offlinepanels":
                    doc.append(f"No painel {label} foram detectadas anomalias indicando painéis desligados conforme as figuras acima.\n")
                elif key == "faultydiodes":
                    doc.append(f"No painel {label} foram detectados diodos de bypass queimados conforme as figuras acima.\n")
        else:
            doc.append(f"As imagens coletadas não detectaram {section_title.lower()} na área inspecionada.\n")

    # --- Append additional statistics if available ---
    if stats:
        # Functions to create various statistics tables are defined below.
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
            table.append(NoEscape(r'\toprule'))
            for row in data:
                table.add_row(row)
            table.append(NoEscape(r'\bottomrule'))
            with doc.create(pl.Center()) as centered:
                with centered.create(pl.Table(position='h!')) as table_with_caption:
                    table_with_caption.add_caption("Processing Statistics")
                    table_with_caption.append(NoEscape(r'\begin{center}'))
                    table_with_caption.append(table)
                    table_with_caption.append(NoEscape(r'\end{center}'))
            return centered

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
            table.append(NoEscape(r'\toprule'))
            for row in data:
                table.add_row(row)
            table.append(NoEscape(r'\bottomrule'))
            with doc.create(pl.Center()) as centered:
                with centered.create(pl.Table(position='h!')) as table_with_caption:
                    table_with_caption.add_caption("Feature Statistics")
                    table_with_caption.append(NoEscape(r'\begin{center}'))
                    table_with_caption.append(table)
                    table_with_caption.append(NoEscape(r'\end{center}'))
            return centered

        def create_reconstruction_stats_table(stats):
            reconstruction_stats = stats['reconstruction_statistics']
            data = [
                ['Components', reconstruction_stats['components']],
                ['Has GPS', reconstruction_stats['has_gps']],
                ['Initial Points Count', reconstruction_stats['initial_points_count']],
                ['Reconstructed Points Count', reconstruction_stats['reconstructed_points_count']]
            ]
            table = pl.Tabular('lr')
            table.append(NoEscape(r'\toprule'))
            for row in data:
                table.add_row(row)
            table.append(NoEscape(r'\bottomrule'))
            with doc.create(pl.Center()) as centered:
                with centered.create(pl.Table(position='h!')) as table_with_caption:
                    table_with_caption.add_caption("Reconstruction Statistics")
                    table_with_caption.append(NoEscape(r'\begin{center}'))
                    table_with_caption.append(table)
                    table_with_caption.append(NoEscape(r'\end{center}'))
            return centered

        def create_gps_errors_table(stats):
            gps_errors = stats['gps_errors']
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
            table = pl.Tabular('lr')
            table.append(NoEscape(r'\toprule'))
            for row in data:
                table.add_row(row)
            table.append(NoEscape(r'\bottomrule'))
            with doc.create(pl.Center()) as centered:
                with centered.create(pl.Table(position='h!')) as table_with_caption:
                    table_with_caption.add_caption("GPS Errors")
                    table_with_caption.append(NoEscape(r'\begin{center}'))
                    table_with_caption.append(table)
                    table_with_caption.append(NoEscape(r'\end{center}'))
            return centered

        doc.append(NoEscape(r'\newpage'))
        doc.append(NoEscape(r'\appendix'))
        doc.append(NoEscape(r'\section{Drone and Flight Information}'))
        doc.append(NoEscape(r'\newcommand{\rotatedimage}[1]{\includegraphics[angle=90, width=0.8\textwidth]{#1}}'))
        top_view_fixed = top_view.replace('\\', '/')
        with doc.create(pl.Figure(position='h!')) as fig:
            fig.append(NoEscape(r'\rotatedimage{' + top_view_fixed + '}'))
        doc.append("Drone Flight Information.")
        create_processing_stats_table(stats)

        # Orthophoto Data section
        doc.append(NoEscape(r'\section{Orthophoto Data}'))
        with doc.create(pl.Figure(position='h!')) as fig:
            fig.add_image(match)
            fig.add_caption("Match Graph")
        doc.append("Descrição do gráfico.")
        create_gps_errors_table(stats)
        with doc.create(pl.Figure(position='h!')) as fig:
            fig.add_image(overlap)
            fig.add_caption("Overlap Graph")
        doc.append("Descrição do gráfico.")
        create_reconstruction_stats_table(stats)
        with doc.create(pl.Figure(position='h!')) as fig:
            fig.add_image(residual)
            fig.add_caption("Model Residual")
        doc.append("Descrição do gráfico.")
        create_features_stats_table(stats)

    # Return the full LaTeX source as a string
    return doc.dumps()

