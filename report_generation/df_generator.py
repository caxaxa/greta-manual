import pyproj
import pandas as pd



def dict_to_dataframe(affected_panels_coordinate):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(affected_panels_coordinate.items()), columns=['Painel', 'Coordenadas'])
    return df

def transform_coordinates(df):
    # Define source and target coordinate systems
    in_proj = pyproj.Transformer.from_crs('EPSG:32724', 'EPSG:4326', always_xy=True)
    
    # Apply the transformation
    def transform_coords(coord):
        lon, lat = in_proj.transform(coord[0], coord[1])
        return (lon, lat)

    df['Coordenadas Geográficas'] = df['Coordenadas'].apply(transform_coords)

    return df

def create_df(affected_panels_coord):
    df = dict_to_dataframe(affected_panels_coord)

    df_transformed = transform_coordinates(df)

    df = df_transformed


    return df

def save_xls(df, xls_path):
    # Save to an .xls file
    with pd.ExcelWriter(xls_path, engine='openpyxl') as writer:
        df.to_excel(writer)