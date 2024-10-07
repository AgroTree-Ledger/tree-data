import ee
from datetime import datetime
import pandas as pd
from tree_data.growth_metrics import calculate_age, calculate_standard_height_growth_rate, calculate_current_height_growth_rate, calculate_standard_dbh_growth_rate, calculate_current_dbh_growth_rate, estimate_tree_value

def calculate_growth_metrics(age, canopy_height, dbh):
    """
    Calculates growth metrics for height and diameter at breast height (DBH) based on the tree's age.

    Args:
        age (float): The age of the tree in years.
        canopy_height (float): The current height of the tree's canopy.
        dbh (float): The diameter at breast height (DBH) of the tree.

    Returns:
        dict: A dictionary containing the standard and observed growth rates for height and DBH.
    """
    return {
        "standard_growth_rate_height": calculate_standard_height_growth_rate(),
        "observed_growth_rate_height": calculate_current_height_growth_rate(canopy_height, age),
        "standard_growth_rate_dbh": calculate_standard_dbh_growth_rate(),
        "observed_growth_rate_dbh": calculate_current_dbh_growth_rate(dbh, age)
    }

def get_batch(fc_list, start, batch_size, total):
    """
    Retrieves a batch of features from a Google Earth Engine FeatureCollection.

    Args:
        fc_list (ee.List): A list of features in the FeatureCollection.
        start (int): The starting index of the batch.
        batch_size (int): The number of features to include in the batch.
        total (int): The total number of features in the collection.

    Returns:
        ee.FeatureCollection: A FeatureCollection containing the batch of features.
    """
    if batch_size + start > total:
        return ee.FeatureCollection(fc_list.slice(start))
    else:
        return ee.FeatureCollection(fc_list.slice(start, start + batch_size))

def get_tree_data_from_feature(feature, update_date):
    """
    Extracts tree data from a single feature and calculates the tree's growth metrics.

    Args:
        feature (dict): A dictionary representing a single tree feature from the FeatureCollection.
        update_date (str): The current date, used to calculate the tree's age.

    Returns:
        dict: A dictionary containing the tree's data including coordinates, growth metrics,
              canopy height, DBH, estimated value, and CO2 sequestration.
    """
    properties = feature['properties']
    geometry = feature['geometry']['coordinates']
    
    plantation_date = properties.get('plantation_date')
    canopy_height = properties.get('canopy_height')
    canopy_cover_percentage = properties.get('canopy_cover_percentage')
    initial_height = float(properties.get('initial_height', 0.0))
    project_developer = properties.get('project_developer')

    age = calculate_age(plantation_date, update_date)
    dbh = age * 1.5

    growth_metrics = calculate_growth_metrics(age, canopy_height, dbh)

    first_harvest_date = datetime.strptime(plantation_date, "%Y-%m-%d") + pd.DateOffset(years=12)
    second_harvest_date = datetime.strptime(plantation_date, "%Y-%m-%d") + pd.DateOffset(years=24)
    
    return {
        "longitude": geometry[0],
        "latitude": geometry[1],
        "species": "Paulownia",
        "plantation_date": plantation_date,
        "initial_height": f"{initial_height}",
        "age": age,
        "current_height": canopy_height,
        "canopy_cover_percentage": canopy_cover_percentage,
        "current_dbh": dbh,
        "standard_growth_rate_height": growth_metrics['standard_growth_rate_height'],
        "observed_growth_rate_height": growth_metrics['observed_growth_rate_height'],
        "standard_growth_rate_dbh": growth_metrics['standard_growth_rate_dbh'],
        "observed_growth_rate_dbh": growth_metrics['observed_growth_rate_dbh'],
        "first_harvest_date": first_harvest_date,
        "second_harvest_date": second_harvest_date,
        "current_estimated_value": estimate_tree_value(age, 100, 500),
        "current_CO2_sequestration": 1.75 * age,
        "project_developer": project_developer,
        "update_date": update_date
    }

def gee_data_to_df(feature_collection, batch_size=5000):
    """
    Processes a Google Earth Engine FeatureCollection and converts it into a Pandas DataFrame.
    Extracts the tree data in batches to avoid memory overload, calculates growth metrics,
    and returns the data as a DataFrame.

    Args:
        feature_collection (ee.FeatureCollection): The FeatureCollection to process.
        batch_size (int): The number of features to process per batch.

    Returns:
        pd.DataFrame: A DataFrame containing the processed tree data including growth metrics, 
                      canopy height, DBH, and other attributes.
    """
    update_date = datetime.now().strftime("%Y-%m-%d")
    print("Computing growth metrics...")

    fc_list = feature_collection.toList(feature_collection.size())
    total = feature_collection.size().getInfo()
    print(f"Total number of trees: {total}")

    tree_data = []

    for i in range(0, total, batch_size):
        print(f"Batch processing from {i} to {i + batch_size}")
        batch = get_batch(fc_list, i, batch_size, total)
        batch_info = batch.getInfo()['features']
        for feature in batch_info:
            tree_data.append(get_tree_data_from_feature(feature, update_date))
        print(f"Processed batch {i // batch_size + 1}: {len(batch_info)} trees.")

    df = pd.DataFrame(tree_data)
    return df
