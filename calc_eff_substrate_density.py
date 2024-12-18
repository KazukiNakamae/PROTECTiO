import pandas as pd
import argparse

def merge_and_calculate_density(eval_res_path, table_path, output_path):
    # Load the two CSV files
    eval_res_df = pd.read_csv(eval_res_path)
    table_df = pd.read_csv(table_path)

    # Merging the two dataframes based on 'flanking_sequence' column
    merged_df = pd.merge(eval_res_df, table_df, on='flanking_sequence', how='inner')

    # Calculating scalar values
    total_label_1_count = merged_df[merged_df['pred'] == 'LABEL_1'].shape[0]
    total_flanking_sequence_count = merged_df.shape[0]
    amino_acid_len = merged_df['amino_acid_len'].iloc[0]

    # Scalar value 1: (LABEL_1 count) / (flanking_sequence total count) / (amino_acid_len)
    eff_substrate_dens = round(total_label_1_count / total_flanking_sequence_count / amino_acid_len, 5)

    # Scalar value 2: Mean of rel_amino_acid_pos for all rows
    mean_rel_amino_acid_pos_all = round(merged_df['rel_amino_acid_pos'].mean(), 5)

    # Scalar value 3: Mean of rel_amino_acid_pos for rows with LABEL_1
    mean_rel_amino_acid_pos_label_1 = round(merged_df[merged_df['pred'] == 'LABEL_1']['rel_amino_acid_pos'].mean(), 5)

    # Creating a DataFrame to store the results
    density_df = pd.DataFrame({
        'Total substrate': [total_flanking_sequence_count],
        'Effective substrate': [total_label_1_count],
        'Peptide length': [amino_acid_len],
        'Effective substrate density': [eff_substrate_dens],
        'Mean position of Substrate': [mean_rel_amino_acid_pos_all],
        'Mean position of Effective substrate': [mean_rel_amino_acid_pos_label_1]
    })

    # Saving the result to a CSV file
    density_df.to_csv(output_path, index=False)
    print(f"Density calculations saved to {output_path}")

if __name__ == "__main__":
    # Argument parser for command-line arguments
    parser = argparse.ArgumentParser(description='Merge two CSV files and calculate density values.')
    parser.add_argument('-e', '--eval_res', type=str, help='Path to the eval_res.csv file')
    parser.add_argument('-t', '--table', type=str, help='Path to the table.csv file')
    parser.add_argument('-d', '--output', type=str, help='Output path for the density.csv file')

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided arguments
    merge_and_calculate_density(args.eval_res, args.table, args.output)
