import random
import os
import argparse
import pandas as pd

def extract_random_rows(input_file, output_dir, prefix, num_rows, seed):
    # Set the random seed for reproducibility
    random.seed(seed)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Check if the specified number of rows is greater than available rows
    if num_rows > len(df):
        raise ValueError(f"The input file {input_file} has fewer than {num_rows} rows.")

    # Randomly select the specified number of rows
    selected_rows = df.sample(n=num_rows, random_state=seed)

    # Generate the output file path
    output_file = os.path.join(output_dir, f"{prefix}_{num_rows}_{seed}.csv")

    # Write the selected rows to the output file with header
    selected_rows.to_csv(output_file, index=False)

    print(f"Extracted {num_rows} rows from {input_file} to {output_file}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract random rows from input CSV files and save to output directory.")
    parser.add_argument("--output_directory", type=str, help="Directory to save output files")
    parser.add_argument("--neg_file", type=str, help="Path to eval_res_neg.csv file")
    parser.add_argument("--pos_file", type=str, help="Path to eval_res_pos.csv file")
    parser.add_argument("--num_rows", type=int, help="Number of rows to extract")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")

    # Parse arguments
    args = parser.parse_args()

    # Extract rows from both files
    extract_random_rows(args.neg_file, args.output_directory, 'eval_res_neg', args.num_rows, args.seed)
    extract_random_rows(args.pos_file, args.output_directory, 'eval_res_pos', args.num_rows, args.seed)

if __name__ == "__main__":
    main()
