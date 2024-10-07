import ee
import math

def create_grid_within_roi(roi, gridsize):
    """
    Creates a grid of polygons within a region of interest (ROI). The grid cells represent 1-hectare areas
    based on the specified grid size.

    Args:
        roi (ee.Geometry): The region of interest as a Google Earth Engine geometry.
        gridsize (float): The size of each grid cell in meters.

    Returns:
        ee.FeatureCollection: A Google Earth Engine FeatureCollection containing polygons of grid cells 
                              within the specified ROI.
    """
    bounds = roi.bounds().coordinates().getInfo()[0]
    lon_min, lat_min = bounds[0]
    lon_max, lat_max = bounds[2]
    
    meters_per_degree_lat = 111320  # Conversion factor for latitude to meters
    meters_per_degree_lon = meters_per_degree_lat * math.cos(math.radians(lat_min))
    width_deg = gridsize / meters_per_degree_lon
    height_deg = gridsize / meters_per_degree_lat
    
    n_lon = math.ceil((lon_max - lon_min) / width_deg)
    n_lat = math.ceil((lat_max - lat_min) / height_deg)
    print(f"Grid of {n_lon} x {n_lat} of 1-hectare polygons")
    
    lons = ee.List.sequence(0, n_lon - 1)
    lats = ee.List.sequence(0, n_lat - 1)

    def create_cell(lon_idx):
        lon_start = ee.Number(lon_min).add(ee.Number(lon_idx).multiply(width_deg))
        
        def create_cell_lat(lat_idx):
            lat_start = ee.Number(lat_min).add(ee.Number(lat_idx).multiply(height_deg))
            rect = ee.Geometry.Rectangle([
                lon_start,
                lat_start,
                lon_start.add(width_deg),
                lat_start.add(height_deg)
            ])
            clipped = rect.intersection(roi, ee.ErrorMargin(1))
            area = clipped.area(1)
            return ee.Feature(clipped).set('area_m2', area)
        
        return lats.map(create_cell_lat)
    
    grid_features = lons.map(create_cell).flatten()
    grid_fc = ee.FeatureCollection(grid_features).filter(ee.Filter.gt('area_m2', 1))

    return grid_fc

def calculate_canopy_area(bin_canopy, polygon, specie_tree_density):
    """
    Calculates the canopy area and canopy cover percentage within a given polygon, 
    based on the canopy binary image (bin_canopy).

    Args:
        bin_canopy (ee.Image): A binary image where the canopy is represented by high NDVI values.
        polygon (ee.Geometry): The polygon representing a grid cell within the region of interest.
        specie_tree_density (float): The tree density (trees per hectare) for the species being analyzed.

    Returns:
        dict: A dictionary containing the canopy cover area in square meters, the canopy cover percentage, 
              and the estimated number of trees within the polygon.
    """
    bin_polygon = bin_canopy.clip(polygon)

    canopy_area = bin_polygon.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=polygon,
        scale=10,  
        maxPixels=1e9
    ).get('NDVI')
    
    canopy_area = ee.Number(canopy_area).min(polygon.area())
    polygon_area = polygon.area()
    
    canopy_percentage = ee.Number(canopy_area).divide(polygon_area).multiply(100)
    canopy_area_ha = ee.Number(canopy_area).divide(10000)
    number_of_trees = canopy_area_ha.multiply(specie_tree_density)
    
    return {
        'canopy_cover_m2': canopy_area,
        'canopy_cover_percentage': canopy_percentage,
        'tree_density': number_of_trees
    }

def cover_per_hectare(ndvi_image, grid, ndvi_threshold):
    """
    Calculates the canopy cover per hectare for each polygon in the grid, based on the NDVI image 
    and a specified NDVI threshold.

    Args:
        ndvi_image (ee.Image): The NDVI image used to detect canopy cover.
        grid (ee.FeatureCollection): A grid of polygons representing the region of interest.
        ndvi_threshold (float): The NDVI value threshold to differentiate canopy from non-canopy areas.

    Returns:
        ee.FeatureCollection: A FeatureCollection with each polygon updated with canopy cover information.
    """
    bin_canopy = ndvi_image.gt(ndvi_threshold)

    updated_polygons = []

    for polygon in grid.getInfo()['features']:
        polygon_geometry = ee.Geometry.Polygon(polygon['geometry']['coordinates'])
        canopy_data = calculate_canopy_area(bin_canopy, polygon_geometry, specie_tree_density=400)
        updated_polygon = polygon.copy()
        updated_polygon['properties'].update(canopy_data)
        updated_polygons.append(updated_polygon)

    return ee.FeatureCollection(updated_polygons)

def find_trees_in_polygon(polygon, trees):
    """
    Finds the trees located within a given polygon from a tree FeatureCollection.

    Args:
        polygon (ee.Feature): The polygon to check for tree locations.
        trees (ee.FeatureCollection): The FeatureCollection of trees.

    Returns:
        ee.FeatureCollection: A FeatureCollection containing trees that are located within the polygon.
    """
    polygon_geometry = ee.Geometry.Polygon(polygon['geometry']['coordinates'])
    trees_in_polygon = trees.filterBounds(polygon_geometry)
    return trees_in_polygon

def image_ndvi(roi):
    """
    Retrieves the NDVI image for the specified region of interest (ROI) from the Sentinel-2 image collection.

    Args:
        roi (ee.Geometry): The region of interest as a Google Earth Engine geometry.

    Returns:
        ee.Image: An NDVI image for the region of interest.
    """
    image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(roi) \
        .filterDate('2023-01-01', '2023-12-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)) \
        .sort('system:time_start', False) \
        .first()

    nir = image.select('B8')
    red = image.select('B4')
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    return ndvi

def extract_canopy_cover(trees, polygons_filled):
    """
    Updates tree information by performing a spatial join between trees and filled polygons 
    to extract the canopy cover percentage for each tree.

    Args:
        trees (ee.FeatureCollection): The FeatureCollection of trees.
        polygons_filled (ee.FeatureCollection): The FeatureCollection of polygons with canopy cover information.

    Returns:
        ee.FeatureCollection: A FeatureCollection of trees with updated canopy cover percentage information.
    """
    print("Updating tree information using spatial join...")

    spatial_filter = ee.Filter.intersects(
        leftField='.geo',
        rightField='.geo',
        maxError=10
    )
    save_first_join = ee.Join.saveFirst('matched_polygon')
    joined = save_first_join.apply(trees, polygons_filled, spatial_filter)

    def add_pol_properties(feature):
        matched_polygon = ee.Feature(feature.get('matched_polygon'))
        canopy_cover = matched_polygon.get('canopy_cover_percentage')
        return feature.set({'canopy_cover_percentage': canopy_cover})

    joined = joined.map(add_pol_properties)

    return joined
