
import pyproj
import pandas as pd


def dict_to_dataframe(affected_panels_coordinate):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(affected_panels_coordinate.items()), columns=['Painel', 'Coordenadas'])
    return df


def transform_coordinates(df):
    # Define source and target coordinate systems
    in_proj = pyproj.Proj(proj='utm', zone=24, ellps='WGS84', south=True)
    out_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    # Apply the transformation
    df['Coordenadas Geográficas'] = df['Coordenadas'].apply(lambda coord: pyproj.transform(in_proj, out_proj, coord[0], coord[1]))

    return df

