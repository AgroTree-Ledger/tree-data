import ee
import pandas as pd
from shapely.geometry import Point, MultiPoint
from pprint import pprint

def create_trees_feature_collection(points_data):
    """
    Creates a Google Earth Engine (GEE) FeatureCollection from a list of tree points.

    Args:
        points_data (list): A list of dictionaries where each dictionary represents a tree with coordinates, 
                            plantation date, initial height, and project developer information.
    
    Returns:
        ee.FeatureCollection: A Google Earth Engine FeatureCollection containing the trees' coordinates 
                              and associated metadata.
    """
    print("Creating a GEE FeatureCollection...")
    
    trees_collection = ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point([point['point'].x, point['point'].y]), {
            'id': i,
            'plantation_date': point['plantation_date'],
            'initial_height': point['initial_height'],
            'project_developer': point['project_developer']
        }) for i, point in enumerate(points_data)
    ])
    
    return trees_collection

def translate_collection_to_df(feature_collection, properties=[], batch_size=1000):
    """
    Translates a Google Earth Engine FeatureCollection into a Pandas DataFrame, extracting specific properties
    from each feature in the collection in batches.

    Args:
        feature_collection (ee.FeatureCollection): The Google Earth Engine FeatureCollection to be processed.
        properties (list): A list of property names to extract from each feature.
        batch_size (int): The number of features to process per batch to avoid memory issues.
    
    Returns:
        pd.DataFrame: A DataFrame containing the requested properties from the FeatureCollection.
    """
    fc_list = feature_collection.toList(feature_collection.size())
    total = feature_collection.size().getInfo()
    
    tree_data = []
    for i in range(0, total, batch_size):
        print(f"Batch processing from {i} to {i + batch_size}")
        if batch_size + i > total:
            batch = ee.FeatureCollection(fc_list.slice(i))
        else:
            batch = ee.FeatureCollection(fc_list.slice(i, batch_size))
        
        batch_info = batch.getInfo()['features']
        for feature in batch_info:
            feature_properties = feature['properties']
            for property_name in properties:
                property_data = feature_properties.get(f'{property_name}')
                tree_data.append({
                    "canopy_cover_percentage": property_data
                })

        print(f"Processed batch {i//batch_size + 1}: {len(batch_info)} trees.")

    return pd.DataFrame(tree_data)

def extract_points_from_csv(df, initial_height, plantation_date, project_developer, species="Paulownia",):
    """
    Extracts points from a CSV file and constructs a list of dictionaries containing tree information,
    such as location, species, initial height, and plantation details.

    Args:
        df (pd.DataFrame): A Pandas DataFrame containing longitude and latitude columns.
        species (str): The species of the trees. Defaults to "Paulownia".
        initial_height (float): The initial height of the trees. Defaults to 2.0.
        plantation_date (str): The plantation date of the trees. Defaults to "2023-09-15".
        project_developer (str): The developer of the tree plantation. Defaults to "EcoTree Solution".
    
    Returns:
        list: A list of dictionaries where each dictionary contains the coordinates, species, 
              initial height, plantation date, and project developer for each tree.
    """
    points_data = []
    
    for _, row in df.iterrows():
        point = Point(row['longitude'], row['latitude'])
        point_data = {
            'point': point,
            'species': species,
            'initial_height': initial_height,
            'plantation_date': plantation_date,
            'project_developer': project_developer
        }
        points_data.append(point_data)
    return points_data

def extract_roi_from_points(points, wkt_format=False):
    """
    Extracts a region of interest (ROI) as a convex hull from a list of points.

    Args:
        points (list): A list of dictionaries containing point data (longitude and latitude).
        wkt_format (bool): If True, returns the convex hull in WKT (Well-Known Text) format. 
                           If False, returns a Google Earth Engine geometry object.
    
    Returns:
        shapely.geometry.Polygon or ee.Geometry.Polygon: The convex hull of the points as a Shapely Polygon 
                                                         or an Earth Engine Geometry Polygon.
    """
    print("Extracting ROI from data points...")
    multi_point = MultiPoint([point['point'] for point in points])
    convex_hull = multi_point.convex_hull

    if convex_hull.geom_type == 'LineString':
        print("Convex hull is a LineString. Buffering to create a polygon.")
        convex_hull = convex_hull.buffer(0.001)
    
    if wkt_format:
        return convex_hull
    return ee.Geometry.Polygon([list(vertex) for vertex in convex_hull.exterior.coords])
