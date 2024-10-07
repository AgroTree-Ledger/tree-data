from dateutil import parser

GROWTH_SUBSEQUENT_YEARS = 2.0
DBH_GROWTH_SUBSEQUENT_YEARS = 2.5

def calculate_standard_height_growth_rate():
    """
    Calculates the standard growth rate for tree height in subsequent years.

    Returns:
        float: The standard height growth rate, rounded to two decimal places.
    """
    return round(GROWTH_SUBSEQUENT_YEARS, 2)

def calculate_current_height_growth_rate(current_height, age):
    """
    Calculates the current height growth rate based on the current height and the tree's age.

    Args:
        current_height (float): The current height of the tree.
        age (float): The age of the tree in years.

    Returns:
        float: The current height growth rate, rounded to two decimal places, or 0 if age is non-positive.
    """
    if age <= 0 or current_height is None:
        return 0
    return round(current_height / age, 2)

def calculate_standard_dbh_growth_rate():
    """
    Calculates the standard growth rate for diameter at breast height (DBH) in subsequent years.

    Returns:
        float: The standard DBH growth rate, rounded to two decimal places.
    """
    return round(DBH_GROWTH_SUBSEQUENT_YEARS, 2)

def calculate_current_dbh_growth_rate(current_dbh, age):
    """
    Calculates the current DBH growth rate based on the current DBH and the tree's age.

    Args:
        current_dbh (float): The current DBH of the tree.
        age (float): The age of the tree in years.

    Returns:
        float: The current DBH growth rate, rounded to two decimal places, or 0 if age is non-positive.
    """
    if age <= 0:
        return 0
    return round(current_dbh / age, 2)

def calculate_age(plantation_date, update_date):
    """
    Calculates the age of the tree in years based on the plantation date and the current date.

    Args:
        plantation_date (str): The plantation date of the tree (in string format).
        update_date (str): The date on which the age is being calculated (in string format).

    Returns:
        float: The age of the tree in years, rounded to two decimal places.
    """
    plantation = parser.parse(plantation_date)
    update = parser.parse(update_date)
    age_years = (update - plantation).days / 365.25
    return round(age_years, 2)

def estimate_tree_value(age, initial_value, max_value):
    """
    Estimates the current value of a tree based on its age, initial value, and maximum value.

    Args:
        age (float): The age of the tree in years.
        initial_value (float): The initial value of the tree.
        max_value (float): The maximum possible value of the tree.

    Returns:
        float: The estimated value of the tree, rounded to two decimal places.
    """
    if age == 0:
        return initial_value

    value = initial_value + (age * 35)
    
    value = max(value, initial_value)
    value = min(value, max_value)
    
    return round(value, 2)
