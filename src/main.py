import pandas as pd
import argparse
import ee
from tree_data.tree_data_pipeline import tree_data_retrieval

def parse_args():
    parser = argparse.ArgumentParser(description="Update tree metrics")
    
    parser.add_argument("--start_csv", default="data/input/gps_example.csv", type=str, help="Path to the csv file containing the tree gps coordinates")
    parser.add_argument("--final_csv", default="data/output/output_example.csv", type=str, help="Path to store final csv containing the full tree data")
    parser.add_argument("--species", default="Paulownia", type=str, help="Species of the trees")
    parser.add_argument("--plantation_date", default="2023-09-15", type=str, help="Date of plantation")
    parser.add_argument("--initial_height", default=2.0, type=float, help="Initial height of the trees")
    parser.add_argument("--project_developer", default="EcoTree Solution", type=str, help="Project developer name")
    parser.add_argument("--specie_tree_density", default=400, type=int, help="Tree density per hectare")
    
    return parser.parse_args()


def main():
    ee.Authenticate()
    ee.Initialize(project='ee-enjoy0')
    
    args = parse_args()
    
    origin_tree_data = pd.read_csv(args.start_csv)
    
    full_tree_data = tree_data_retrieval(origin_tree_data, args)
    print(full_tree_data.head(5))

    full_tree_data.to_csv(args.final_csv, index=False)



if __name__ == "__main__":
    main()