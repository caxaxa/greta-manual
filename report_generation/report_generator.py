import pylatex as pl
from pylatex.utils import NoEscape, bold
from datetime import datetime
import os

def generate_report(df, language="pt"):

    # Get the current directory of the script

    author_dict = {"Lucas Chacha": "Técnico de IA"}
    area_name = "Nome da Área"
    intro_text_pt = 'teste'
    client_data = "Client data here..."
    text_3_1_pt = "Text for section 3..."
    orthophoto_path_img = ('report_images/ortho.png')
    aisol_logo_path = ('report_images/aisol_logo.png' )
    aisol_logo_2_path = ('report_images/logo_2.png' )
    #df = # created in the main app
    layer_img_path = ('report_images/layer_img.png' )
    text_4_1_pt = "Text for section 4..."
    top_view =  ("report_images/topview.png")
    match =  ("report_images/matchgraph.png")
    overlap =  ("report_images/overlap.png")
    residual =  ("report_images/residual_histogram.png")
    stats =  ("report_images/stats.json")

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
    doc.preamble.append(NoEscape(r'\fancyhead[R]{Relatório de Imagens Térmicas}'))
    doc.preamble.append(NoEscape(r'\fancyfoot[C]{GRETA® System, Beta Version - 2023         Powered by Aisol ®}'))
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
    {\fontsize{60}{72} \selectfont {{Relatório Termografia}}} \\[1cm]
    {\fontsize{16}{19.2} \selectfont \textcolor{RoyalBlue}{ \bf Relatório de Área}}\\[3pt]
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
    doc.append(NoEscape(r'{\large\bfseries Relatório Técnico de Inspeção}'))
    doc.append(NoEscape(r'\vspace*{0.5cm}'))
    doc.append(NoEscape(r'\textbf{Responsável Técnico:} Fábio Corpa, Engenheiro'))
    doc.append(NoEscape(r'\textbf{CREA:} 12345678'))
    doc.append(NoEscape(r'\textbf{Data:} Outubro 2023'))
    doc.append(NoEscape(r'\textbf{Localização:} Campo Grande, MS. Brasil'))
    doc.append(NoEscape(r'\textbf{Endereço:} Rua Manoel Inácio de Souza, n. 24, C.E.P : 79.020-220'))
    doc.append(NoEscape(r'\textbf{Software:} GRETA® - Georeferenced Thermal Analysis System, Beta Version'))
    doc.append(NoEscape(r'\textbf{Versão:} Versao do Cliente'))
    doc.append(NoEscape(r'\end{center}'))

    # Spacer
    doc.append(NoEscape(r'\vspace*{0.4cm}'))

    # Line separator
    doc.append(NoEscape(r'\rule{\linewidth}{0.5pt}'))

    # Bottom part with copyrights
    doc.append(NoEscape(r'\vfill'))
    doc.append(NoEscape(r'\noindent\textbf{Copyright © 2023 Aisol Solucoes em Inteligência Artificial}'))
    doc.append(NoEscape(r'All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, without the prior written permission of the publisher.'))
    doc.append(NoEscape(r'\vspace*{0.2cm}'))
    doc.append(NoEscape(r'\noindent\textbf{ISBN:} 123-456-789-0'))


    # Other relevant data
    doc.append(bold("Location:"))
    doc.append("Campo Grande, MS. Brasil")
    doc.append("Rua Manoel Inácio de Souza, n. 24")
    doc.append("C.E.P : 79.020-220")
    doc.append(bold("Copyrights:"))
    doc.append("Aisol, 2023.")
    doc.append(bold("Release:"))
    doc.append("Versao do Cliente")
    doc.append(bold("Company:"))
    doc.append("Aisol Solucoes em Inteligência Artificial")

    # Abstract
    doc.append(NoEscape(r'\newpage'))
    doc.append(NoEscape(r'\begin{abstract}'))
    doc.append(NoEscape(r'Your abstract here.'))
    doc.append(NoEscape(r'\end{abstract}'))

    doc.append(NoEscape(r'\pagestyle{fancy}'))

    # Table of contents, figures, and tables
    doc.append(NoEscape(r'\tableofcontents'))
    #doc.append(NoEscape(r'\listoffigures'))
    doc.append(NoEscape(r'\listoftables'))




    # Main Content
    doc.append(NoEscape(r'\section{Intro}'))
    doc.append(intro_text_pt)
    doc.append(NoEscape(r'\section{Dados do Cliente}'))
    doc.append(client_data)
    doc.append(NoEscape(r'\section{Área %s}' % area_name))
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
                table.add_caption("Tabela de Elementos Encontrados")
              # End centering
        doc.append(NoEscape(r'\FloatBarrier'))
        with doc.create(pl.Figure(position='h!')) as fig:
            fig.add_image(layer_img_path)
            fig.add_caption("Numeracao das Placas com Defeito")
        doc.append(NoEscape(r'\FloatBarrier'))
        doc.append(NoEscape(r'\newpage'))      
        doc.append(NoEscape(r'\section{Detalhamento dos Pontos Térmicos Encontrados}'))
        doc.append(text_4_1_pt)
        for _, row in df.iterrows():
            doc.append(NoEscape(r'\subsection{%s}' % row['Painel']))  
            doc.append(NoEscape(f"\\begin{{figure}}[h!]\\centering\\includegraphics[width=0.48\\linewidth]{{{'report_images/' + row['Nome das Imagens']}}}\\hfill\\includegraphics[width=0.48\\linewidth]{{{'report_images/' + (row['Nome das Imagens']).replace('_MASKED', '_T' )}}}\\caption{{{f'Painel ' + row['Painel']}}}\\label{{fig:my_label}}\\end{{figure}}"))
            doc.append(NoEscape(r'\FloatBarrier'))
            doc.append(NoEscape(f"Descrever erro no painel {row['Painel']} localizado na coordenada {row['Coordenadas Geográficas']}."))
    else:
        doc.append("No affected panels.")
        return doc.dumps()
    
    doc.append(NoEscape(r'\newpage'))
    doc.append(NoEscape(r'\appendix'))
    doc.append(NoEscape(r'\section{Plano de Voo}'))
    doc.append(NoEscape(r'\newcommand{\rotatedimage}[1]{\includegraphics[angle=270, width=0.8\textwidth]{#1}}'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.append(NoEscape(r'\rotatedimage{' + top_view + '}'))
    doc.append(NoEscape(r'\FloatBarrier'))
    doc.append("Descricao do Plano de voo.")

    # Orthophoto Data (to be created)
    doc.append(NoEscape(r'\section{Orthophoto Data}'))
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(match)
        fig.add_caption("Match Graph")
    doc.append("Descricao do gafico.")
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(overlap)
        fig.add_caption("Overlap Graph")
    doc.append("Descricao do gafico.")
    with doc.create(pl.Figure(position='h!')) as fig:
        fig.add_image(residual)
        fig.add_caption("Resíduos do Modelo")
    doc.append("Descricao do gafico.")
    # add orthophoto data here



    return doc.dumps()


