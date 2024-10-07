# Tree Data Retrieval from GPS Coordinates

## Overview

This repository contains a program that aimed at retrieving and processing data for tree plantations using their GPS coordinates. The project leverages satellite imagery and geospatial data to extract essential metrics such as canopy cover, canopy height, and growth rates. It is designed to be open-source, facilitating collaboration and further development.

## Features

- **GPS-Based Data Retrieval**: Extracts tree data based on provided GPS coordinates.
- **Canopy Analysis**: Calculates canopy cover and canopy height using satellite imagery.
- **Growth Metrics**: Estimates growth rates, tree age, diameter at breast height (DBH) and CO₂ sequestration.
- **Batch Processing**: Efficiently handles large datasets by processing data in batches.

## Directory Structure

```
├── src
├── data
│   ├── input
│   │   └── gps_example.csv
│   └── output
│       └── output_example.csv
├── .config
│   └── google_earth_engine
│       └── credentials
├── requirements.txt
└── LICENSE
```

- **src/**: Contains the source code for data retrieval and processing.
- **data/**: Holds input CSV files with GPS coordinates and output CSV files with processed tree data.
- **.config/**: Stores configuration files for authentication (excluded from version control).

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/tree-data-retrieval.git
   cd tree-data-retrieval
   ```
2. **Create a virtual environment**
   
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. **Install dependencies**
   
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Google Earth Engine**

   - Ensure you have a [Google Earth Engine](https://earthengine.google.com/) account.
   - Create a `.env` file at the root of the project and add your GEE project ID:
     ```env
     GEE_PROJECT=your-gcp-project-id
     ```
   - Obtain your Google Earth Engine credentials:
     - Run the following commands in your terminal to authenticate and generate the `credentials` file:
       ```bash
       earthengine authenticate
       ```
   - Place your `credentials` file in the `.config/google_earth_engine/` directory.
   - **Note**: The `.env` file and `.config` directory are excluded from version control for security reasons.


## Usage

The main script allows you to update tree metrics by processing a CSV file containing GPS coordinates.

### Command-Line Arguments

- `--start_csv`: Path to the input CSV file with tree GPS coordinates. *(Default: `data/input/gps_example.csv`)*
- `--final_csv`: Path to save the output CSV file with processed tree data. *(Default: `data/output/output_example.csv`)*
- `--plantation_date`: Date of plantation in `YYYY-MM-DD` format.
- `--initial_height`: Initial height of the trees in meters.
- `--project_developer`: Name of the project developer.

### Running the Script

```bash
python src/main.py \
    --start_csv data/input/your_coords.csv \
    --final_csv data/output/your_output.csv \
    --plantation_date 2022-05-20 \
    --initial_height 1.5 \
    --project_developer "GreenEarth Initiative"
```

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- Developed as part of a Solana hackathon project.
- Utilizes [Google Earth Engine](https://earthengine.google.com/) for geospatial data processing.
- Thanks to the open-source community for their invaluable tools and libraries.

   
