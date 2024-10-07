from tree_data.canopy_cover import cover_per_hectare, image_ndvi, extract_canopy_cover, create_grid_within_roi
from tree_data.canopy_height import height_canopy_image, find_tree_pixel_height
from utils import create_trees_feature_collection, extract_points_from_csv, extract_roi_from_points
from tree_data.collect_data import gee_data_to_df

def update_canopy_height(roi_gee, fc):
    """
    Updates the canopy height of trees within a region of interest (ROI) by querying
    the height from the Google Earth Engine (GEE) using a canopy height image.

    Args:
        roi_gee (ee.Geometry): The region of interest as a Google Earth Engine geometry.
        fc (ee.FeatureCollection): A GEE FeatureCollection containing tree information.
    
    Returns:
        ee.FeatureCollection: A FeatureCollection with updated canopy height information 
                              for each tree in the region of interest.
    """
    print("Updating canopy height...")
    
    image = height_canopy_image(roi_gee)
    canopy_height_fc = fc.map(lambda feature: find_tree_pixel_height(feature, image))
    return canopy_height_fc

def update_canopy_cover(roi_gee, fc):
    """
    Updates the canopy cover percentage for trees within a region of interest (ROI)
    by calculating the NDVI and using grid-based calculations to estimate canopy cover.

    Args:
        roi_gee (ee.Geometry): The region of interest as a Google Earth Engine geometry.
        fc (ee.FeatureCollection): A GEE FeatureCollection containing tree information.
    
    Returns:
        ee.FeatureCollection: A FeatureCollection with updated canopy cover percentage
                              for each tree in the region of interest.
    """
    print("Updating canopy cover...")
    
    grid = create_grid_within_roi(roi_gee, gridsize=100)
    ndvi_image = image_ndvi(roi_gee)
    polygons_filled = cover_per_hectare(ndvi_image, grid, ndvi_threshold=0.4)
    
    canopy_cover_fc = extract_canopy_cover(fc, polygons_filled)
    return canopy_cover_fc

def tree_data_retrieval(df, args):
    """
    Retrieves tree data from a DataFrame and updates the canopy height and cover
    for each tree within the region of interest (ROI). The result is processed and
    returned as a Pandas DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing longitude, latitude, and other tree data.
        args: An object containing user-provided arguments such as species, initial height,
              plantation date, and project developer.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the updated tree data with canopy height,
                      canopy cover, and other relevant metrics.
    """
    print("Retrieval of tree's data...")
    
    data_list = extract_points_from_csv(df, args.initial_height, args.plantation_date, args.project_developer)
    roi_gee = extract_roi_from_points(data_list, wkt_format=False)
    trees_collection = create_trees_feature_collection(data_list)
    
    trees_with_height = update_canopy_height(roi_gee, trees_collection)
    trees_with_canopy_cover = update_canopy_cover(roi_gee, trees_with_height)
    
    data = gee_data_to_df(trees_with_canopy_cover)
    return data
