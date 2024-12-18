import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
from statsmodels.stats.power import TTestIndPower
import argparse

# Function to read and combine CSV files from a directory
def load_and_combine_data(files):
    data_frames = []
    for file in files:
        df = pd.read_csv(file).iloc[:, 1:]  # Skip the first two columns
        tissue = os.path.basename(file).split('.')[0]  # Extract tissue name from filename
        tissue = '_'.join(tissue.split('_')[1:])
        df['Tissue'] = tissue  # Add tissue column
        data_frames.append(df)
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df

# Function to generate vertical violin plots for each column and ensure "All" is the first category
def generate_violinplots(df, output_dir):
    value_columns = df.columns[(df.columns != 'ENST_ID') & (df.columns != 'Tissue')]  # All columns except 'Tissue'
    for column in value_columns:
        plt.figure(figsize=(8, 12))  # Vertical violin plot with tall figure size
        
        # Ensure "All" is the leftmost category
        df['Tissue'] = pd.Categorical(df['Tissue'], categories=['All'] + sorted([t for t in df['Tissue'].unique() if t != 'All']))

        # Create a violin plot
        sns.violinplot(x='Tissue', y=column, data=df)
        plt.title(f'Violin plot of {column} across tissues')
        plt.xticks(rotation=90)
        plt.tight_layout()
        
        # Save the plot as a 350dpi PNG
        plt.savefig(os.path.join(output_dir, f'{column}_violinplot.png'), dpi=350)
        plt.close()

# Function to calculate statistics and generate circular bar plots with SEM
def generate_circular_barplot(df, output_dir):
    value_columns = df.columns[(df.columns != 'ENST_ID') & (df.columns != 'Tissue')]
    for column in value_columns:
        # Calculate mean, SEM, and sample size for each tissue, excluding "All"
        stats_data = df[df['Tissue'] != 'All'].groupby('Tissue')[column].agg(
            Mean='mean',
            SEM=lambda x: stats.sem(x, nan_policy='omit'),
            N='count'
        ).reset_index()
        if stats_data.empty or stats_data['N'].sum() == 0:
            # Skip if no valid data is present for the column
            print(f"Skipping {column} due to lack of valid data.")
            continue

        # Save the statistics to a CSV file
        stats_data.to_csv(os.path.join(output_dir, f'{column}_tissue_stats.csv'), index=False)

        # Generate Circular Barplot without "All"
        labels = stats_data['Tissue']
        if labels.empty:
            print(f"Skipping {column} circular plot due to lack of labels.")
            continue
        
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()  # Create angles for each tissue
        values = stats_data['Mean'].fillna(0)
        sem_values = stats_data['SEM'].fillna(0)

        if len(values) == 0 or len(angles) == 0:
            print(f"Skipping {column} circular plot due to missing values.")
            continue

        fig, ax = plt.subplots(figsize=(16, 8), subplot_kw=dict(polar=True))

        # Use a colormap for different tissue colors
        colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))

        # Plot the bars for each tissue
        bars = ax.bar(angles, values, yerr=sem_values, width=0.3, color=colors, alpha=0.7, edgecolor='black', capsize=5)

        # Add labels for each tissue, leaving space for "All"
        ax.set_xticks(angles)
        ax.set_xticklabels([])
        ax.tick_params(axis='x', which='both', length=0)  # Set tick length to 0 to hide the tick marks

        # Add a legend on the right side
        ax.legend(bars, labels, bbox_to_anchor=(1.05, 1), loc='upper left', title="Tissues")

        # Remove the "All" position and place axis labels there
        ax.text(0, 0, "Tissues", va='center', ha='center', fontsize=14, weight='bold')

        plt.title(f'Circular Barplot of {column} with SEM')

        # Save the circular barplot
        plt.savefig(os.path.join(output_dir, f'{column}_circular_barplot.png'), dpi=350)
        plt.close()

def generate_barplot(df, output_dir):
    value_columns = df.columns[(df.columns != 'ENST_ID') & (df.columns != 'Tissue')]
    for column in value_columns:
        # 各ティッシュに対して平均、SEM、およびサンプルサイズを計算（"All" を除く）
        stats_data = df.groupby('Tissue')[column].agg(
            Mean='mean',
            SEM=lambda x: stats.sem(x, nan_policy='omit'),
            N='count'
        ).reset_index()
        if stats_data.empty or stats_data['N'].sum() == 0:
            # 有効なデータがない場合はスキップ
            print(f"Skipping {column} due to lack of valid data.")
            continue

        # 統計をCSVファイルに保存
        stats_data.to_csv(os.path.join(output_dir, f'{column}_tissue_stats_barplot.csv'), index=False)

        # "All"が先頭に来て、"v<数字>"の昇順で並ぶようにソート
        stats_data['Tissue'] = pd.Categorical(
            stats_data['Tissue'],
            categories=['All'] + sorted(
                [t for t in stats_data['Tissue'].unique() if t != 'All'],
                key=lambda x: (int(x.split('_')[0][1:]) if x.startswith('v') else float('inf'))
            ),
            ordered=True
        )
        stats_data = stats_data.sort_values('Tissue')

        # 通常のバーグラフを生成
        labels = stats_data['Tissue']
        values = stats_data['Mean'].fillna(0)
        sem_values = stats_data['SEM'].fillna(0)

        if len(values) == 0:
            print(f"Skipping {column} bar plot due to missing values.")
            continue

        # viridis カラーマップを使って色を生成
        colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))

        # バープロットの描画
        fig, ax = plt.subplots(figsize=(12, 6))

        # バーの描画
        bars = ax.bar(labels, values, yerr=sem_values, capsize=5, color=colors, edgecolor='black')

        # グラフの装飾
        ax.set_title(f'Barplot of {column} with SEM', fontsize=16)
        ax.set_xlabel('Tissue', fontsize=14)
        ax.set_ylabel(f'{column} (Mean ± SEM)', fontsize=14)

        # バーラベルを自動調整
        plt.xticks(rotation=45, ha='right')

        # ファイルに保存
        plt.tight_layout()  # レイアウトを調整してラベルが切れないようにする
        plt.savefig(os.path.join(output_dir, f'{column}_barplot.png'), dpi=350)
        plt.close()

# Function to calculate confidence intervals and extract significant rows
def extract_significant_rows(df, tissue, column, output_dir, alpha):
    # Filter "All" tissue data
    tissue_df = df[df['Tissue'] == tissue]
    all_values = df[df['Tissue'] == 'All'][column].dropna()
    
    # Calculate confidence interval for "All" based on adjusted alpha
    mean_all = np.mean(all_values)
    sem_all = stats.sem(all_values)
    ci = stats.t.interval(1 - alpha, len(all_values) - 1, loc=mean_all, scale=sem_all)

    # Filter data for rows above the upper bound
    upper_df = tissue_df[(tissue_df[column] > ci[1])]
    if not upper_df.empty:
        upper_df.to_csv(os.path.join(output_dir, f'{tissue}_{column}_upper_outliers.csv'), index=False)
        upper_metascape_df = pd.DataFrame({
            "Gene":upper_df['ENST_ID'],
            "OptionalDataColumns":upper_df[column]
        })
        upper_metascape_df.to_csv(os.path.join(output_dir, f'{tissue}_{column}_upper_outliers_for_metascape.csv'), index=False)

    # Filter data for rows below the lower bound
    lower_df = tissue_df[(tissue_df[column] < ci[0])]
    if not lower_df.empty:
        lower_df.to_csv(os.path.join(output_dir, f'{tissue}_{column}_lower_outliers.csv'), index=False)
        lower_metascape_df = pd.DataFrame({
            "Gene":lower_df['ENST_ID'],
            "OptionalDataColumns":lower_df[column]
        })
        lower_metascape_df.to_csv(os.path.join(output_dir, f'{tissue}_{column}_lower_outliers_for_metascape.csv'), index=False)


# Function to perform Welch's t-test with power-adjusted alpha
def perform_welchs_ttest_with_power_adjusted_alpha(df, output_dir, desired_power=0.8):
    value_columns = df.columns[(df.columns != 'ENST_ID') & (df.columns != 'Tissue')]
    power_analysis = TTestIndPower()
    
    for column in value_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
        grouped_data = df.groupby('Tissue')[column].apply(list).to_dict()

        if 'All' in grouped_data:
            all_data = [val for val in grouped_data['All'] if pd.notna(val)]
            
            if len(all_data) > 1:
                column_log_file = os.path.join(output_dir, f'{column}_welch_ttest_results.log')
                with open(column_log_file, 'w') as log:
                    log.write(f"Welch's t-test results for {column}, comparing All vs other tissues:\n")

                    for tissue, data in grouped_data.items():
                        if tissue != 'All':
                            other_tissue_data = [val for val in data if pd.notna(val)]
                            
                            if len(other_tissue_data) > 1:
                                # Perform Welch's t-test
                                ttest_result = stats.ttest_ind(other_tissue_data, all_data, equal_var=False)
                                
                                # Determine adjusted alpha based on desired power
                                alpha = 0.05  # Default
                                enable_power_adjustment = False# May be too strict
                                if enable_power_adjustment:
                                    # Calculate effect size
                                    pooled_std = np.sqrt(np.var(all_data) / len(all_data) + np.var(other_tissue_data) / len(other_tissue_data))
                                    effect_size = abs(np.mean(all_data) - np.mean(other_tissue_data)) / pooled_std
                                    if effect_size > 0:
                                        try:
                                            alpha = 1.0 - power_analysis.solve_power(effect_size=effect_size, power=desired_power, nobs1=len(all_data), ratio=len(other_tissue_data) / len(all_data), alternative='two-sided')
                                            log.write(f"Set alpha level with power={desired_power:.10f}.\n")
                                        except:
                                            log.write(f"Unable to calculate adjusted alpha for {tissue} vs All due to insufficient effect size or sample size.\n")
                                            pass  # Use default alpha if power calculation fails

                                log.write(f'Comparing {tissue} vs All with alpha={alpha:.10f}:\n')
                                log.write(f'  t-statistic: {ttest_result.statistic}, p-value: {ttest_result.pvalue}\n')

                                # Check for statistical significance
                                if ttest_result.pvalue < alpha:
                                    log.write(f'  Statistically significant difference (p-value < {alpha:.10f})\n')
                                    # Extract and save rows outside confidence interval with adjusted alpha
                                    extract_significant_rows(df, tissue, column, output_dir, alpha)
                                else:
                                    log.write(f'  No statistically significant difference (p-value >= {alpha:.10f})\n')
                                log.write('-' * 50 + '\n')
                            else:
                                log.write(f"Not enough data to compare All vs {tissue}.\n")
                                log.write('-' * 50 + '\n')
            else:
                print(f"Skipping {column} due to insufficient data for All.")
        else:
            print(f"Skipping {column} because All data is not available.")

# Updated process_and_analyze_data function
def process_and_analyze_data(input_dir, output_dir):
    # Find all CSV files in the input directory that start with 'rawdata_'
    files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.startswith('rawdata_')]
    
    # Load and combine the data
    combined_df = load_and_combine_data(files)

    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate violin plots for each column
    generate_violinplots(combined_df, output_dir)

    # Generate circular bar plots with SEM and save stats
    generate_circular_barplot(combined_df, output_dir)
    generate_barplot(combined_df, output_dir)

    # Perform Welch's t-test and log results
    perform_welchs_ttest_with_power_adjusted_alpha(combined_df, output_dir)

    print(f"Processing complete. Violin plots, circular barplots, statistics, and Welch's t-test results are saved in: {output_dir}")

# Command-line entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate CSV files, generate violin plots, circular barplots, and perform Welch's t-test.")
    parser.add_argument('--input_dir', required=True, help="Directory containing the CSV files.")
    parser.add_argument('--output_dir', required=True, help="Directory to save plots, statistics, and t-test results.")
    
    args = parser.parse_args()
    
    # Call the main function
    process_and_analyze_data(args.input_dir, args.output_dir)
