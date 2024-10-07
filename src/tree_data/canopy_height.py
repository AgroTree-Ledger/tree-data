import ee

def height_canopy_image(roi):
    """
    Retrieves and clips the canopy height image from Google Earth Engine (GEE)
    for the specified region of interest (ROI).

    Args:
        roi (ee.Geometry): The region of interest as a Google Earth Engine geometry.

    Returns:
        ee.Image: A GEE image representing the canopy height, clipped to the specified ROI.
    """
    image = ee.ImageCollection('projects/meta-forest-monitoring-okw37/assets/CanopyHeight').mosaic()
    return image.clip(roi)


def find_tree_pixel_height(feature, image):
    """
    Finds the canopy height for a given tree feature by querying the pixel value from the canopy height image.

    Args:
        feature (ee.Feature): A GEE feature representing the tree.
        image (ee.Image): A GEE image representing the canopy height.

    Returns:
        ee.Feature: The tree feature with the canopy height added to its properties.
    """
    height = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=feature.geometry(),
        scale=1.2
    ).get('cover_code')
    return feature.set('canopy_height', height)
