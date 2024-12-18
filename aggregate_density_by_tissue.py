import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def collect_values_by_refseqid(filtered_refex_df, base_dir, prefix):
    raw_data_records = []
    # Iterate over the filtered rows
    for _, row in filtered_refex_df.iterrows():
        ncbi_refseq_id = row['NCBI_RefSeqID']
        
        # Search for the NM/NR directory matching the NCBI_RefSeqID
        ncbi_dir_path = os.path.join(base_dir, 'prediction_targets', ncbi_refseq_id)
        
        if os.path.exists(ncbi_dir_path):
            # Iterate over subdirectories (ENSTxxxx)
            enst_dir_list = [f for f in os.listdir(ncbi_dir_path) if not f.startswith('.')]
            for enst_dir in enst_dir_list:
                enst_dir_path = os.path.join(ncbi_dir_path, enst_dir)
                density_file_path = os.path.join(enst_dir_path, prefix + 'density.csv')
                
                # If density.csv exists, read it
                if os.path.exists(density_file_path):
                    density_df = pd.read_csv(density_file_path)
                    # Add to raw data records
                    raw_data_records.append({
                        'NCBI_RefSeqID': ncbi_refseq_id,
                        'ENST_ID': enst_dir,
                        'Total substrate': density_df['Total substrate'].tolist()[0],
                        'Effective substrate': density_df['Effective substrate'].tolist()[0],
                        'Peptide length': density_df['Peptide length'].tolist()[0],
                        'Effective substrate density': density_df['Effective substrate density'].tolist()[0],
                        'Mean position of Substrate': density_df['Mean position of Substrate'].tolist()[0],
                        'Mean position of Effective substrate': density_df['Mean position of Effective substrate'].tolist()[0]
                    })
    return raw_data_records

# Function to process data
def process_density_data(refex_file, base_dir, output_dir, prefix):
    # Make output directory
    os.makedirs(output_dir, exist_ok=False)

    # Load RefEx data
    refex_df = pd.read_csv(refex_file, sep='\t')

    # Columns representing different tissues
    tissue_columns = refex_df.columns[2:]  # From v1_cerebrum to v40_salivary
    tissue_columns = [t.replace(' ', '_') for t in tissue_columns]
    tissue_columns = [t.replace('/', '_') for t in tissue_columns]
    refex_df.columns = refex_df.columns[:2].to_list() + tissue_columns

    all_tissue_specific_transcripts_cnt = len(refex_df)
    print(f'All tissue-specific {all_tissue_specific_transcripts_cnt} transcripts are expressing...')
    if all_tissue_specific_transcripts_cnt > 0:
        all_raw_data_records = collect_values_by_refseqid(refex_df, base_dir, prefix)
        # Convert raw data to DataFrame and save raw data to CSV for the current tissue
        all_raw_data_df = pd.DataFrame(all_raw_data_records)
        all_raw_data_df.to_csv(os.path.join(output_dir, f'rawdata_All.csv'), index=False)
        all_value_columns = all_raw_data_df.columns[2:]

        # Create violin plots for each column in the current tissue's data
        for value_column in all_value_columns:
            values = all_raw_data_df[value_column].to_list()
            if values:
                # Calculate min and max values
                # min_value = min(values)
                # max_value = max(values)

                # Create a violin plot for the column
                plt.figure(figsize=(10, 6))
                sns.violinplot(x=values)
                plt.title(f'{value_column} Distribution in all tissue specific transcripts')
                plt.xlabel(value_column)

                # Set x-axis limits based on min and max values
                # plt.xlim([min_value, max_value])

                # Save the plot as a 350dpi PNG
                plt.savefig(os.path.join(output_dir, f'All_{value_column}_violinplot.png'), dpi=350)
                plt.close()

            # Compute statistical summary
            density_series = pd.Series(values)
            stats = density_series.describe()

            # Save stats to CSV for the current tissue and column
            stats.to_csv(os.path.join(output_dir, f'All_{value_column}_stat.csv'), header=['Value'])
    else:
        print(f'Skipping')
    
    # Iterate over each tissue column
    for tissue_column in tissue_columns:
        # Filter rows where the current tissue column has a value of 1
        filtered_refex_df = refex_df[refex_df[tissue_column] == 1]
        tissue_specific_transcripts_cnt = len(filtered_refex_df)
        print(f'{tissue_column}:Tissue-specific {tissue_specific_transcripts_cnt} transcripts are expressing...')

        if tissue_specific_transcripts_cnt > 0:
            raw_data_records = collect_values_by_refseqid(filtered_refex_df, base_dir, prefix)
            # Convert raw data to DataFrame and save raw data to CSV for the current tissue
            raw_data_df = pd.DataFrame(raw_data_records)
            raw_data_df.to_csv(os.path.join(output_dir, f'rawdata_{tissue_column}.csv'), index=False)
            value_columns = raw_data_df.columns[2:]

            # Create violin plots for each column in the current tissue's data
            for value_column in value_columns:
                values = raw_data_df[value_column].to_list()
                if values:
                    # Calculate min and max values
                    # min_value = min(values)
                    # max_value = max(values)

                    # Create a violin plot for the column
                    plt.figure(figsize=(10, 6))
                    sns.violinplot(x=values)
                    plt.title(f'{value_column} Distribution in {tissue_column}')
                    plt.xlabel(value_column)

                    # Set x-axis limits based on min and max values
                    # plt.xlim([min_value, max_value])

                    # Save the plot as a 350dpi PNG
                    plt.savefig(os.path.join(output_dir, f'{tissue_column}_{value_column}_violinplot.png'), dpi=350)
                    plt.close()

                # Compute statistical summary
                density_series = pd.Series(values)
                stats = density_series.describe()

                # Save stats to CSV for the current tissue and column
                stats.to_csv(os.path.join(output_dir, f'{tissue_column}_{value_column}_stat.csv'), header=['Value'])
        else:
            print(f'Skipping')

    print(f"Processing complete. Outputs saved in: {output_dir}")

# Main entry point
if __name__ == "__main__":
    # Define argument parser
    parser = argparse.ArgumentParser(description="Process density data based on RefEx data and save results.")
    
    # Add arguments for input files and directories
    parser.add_argument('--refex_file', required=True, help="Path to the RefEx_rnaseq.tsv file.")
    parser.add_argument('--base_dir', required=True, help="Base directory containing NM/NRxxxxxx directories.")
    parser.add_argument('--output_dir', required=True, help="Directory to save output files (plots and stats).")
    parser.add_argument('--prefix', required=False, default="", help="Directory to save output files (plots and stats).")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the processing function with parsed arguments
    process_density_data(args.refex_file, args.base_dir, args.output_dir, args.prefix)
