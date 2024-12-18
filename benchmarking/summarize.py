import pandas as pd
import glob
import os
import sys
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns

def main(data_dir, summary_output_path, t_test_output_path, plot_output_dir):
    # Get all CSV files in the specified directory
    file_paths = glob.glob(os.path.join(data_dir, "*_metrics_output.csv"))

    # Read all CSV files into a single DataFrame
    df = pd.concat([pd.read_csv(file) for file in file_paths])

    # Group data by 'condition' and 'classifier' and calculate mean and std for each metric
    summary = df.groupby(['condition', 'classifier']).agg(
        Accuracy_mean=('Accuracy', 'mean'),
        Accuracy_std=('Accuracy', 'std'),
        Precision_mean=('Precision', 'mean'),
        Precision_std=('Precision', 'std'),
        Recall_mean=('Recall', 'mean'),
        Recall_std=('Recall', 'std'),
        F1Score_mean=('F1 Score', 'mean'),
        F1Score_std=('F1 Score', 'std'),
        MCC_mean=('MCC', 'mean'),
        MCC_std=('MCC', 'std')
    ).reset_index()

    # Save summary to CSV file
    summary.to_csv(summary_output_path, index=False)

    # Welch's t-test results
    results = []
    conditions = df['condition'].unique()
    classifiers = df['classifier'].unique()

    for metric in ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'MCC']:
        for cond1 in conditions:
            for clf1 in classifiers:
                group1 = df[(df['condition'] == cond1) & (df['classifier'] == clf1)][metric]
                for cond2 in conditions:
                    for clf2 in classifiers:
                        if (cond1, clf1) < (cond2, clf2):  # to avoid duplicate comparisons
                            group2 = df[(df['condition'] == cond2) & (df['classifier'] == clf2)][metric]
                            if len(group1) > 1 and len(group2) > 1:
                                t_stat, p_value = ttest_ind(group1, group2, equal_var=False)
                                if p_value < 0.05:
                                    results.append(f"Significant difference in {metric} between {cond1}-{clf1} and {cond2}-{clf2} (p-value: {p_value:.4f})")

    # Save t-test results to text file
    with open(t_test_output_path, 'w') as f:
        for line in results:
            f.write(line + '\n')

    print("Summary and t-test results saved.")

    # Set the order of classifiers for plotting
    classifier_order = ['ACWpred', 'WCWpred', 'sv1pred', 'snv1pred']

    # Plot each metric with boxplot
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'MCC']
    for metric in metrics:
        plt.figure(figsize=(6, 10))
        
        # Create a boxplot for each metric by condition and classifier
        sns.boxplot(
            data=df,
            x='condition',
            y=metric,
            hue='classifier',
            hue_order=classifier_order
        )

        plt.ylim(0, 1.0)  # Set y-axis limit to 1.2
        plt.title(f'{metric} by Condition and Classifier')
        plt.ylabel(metric)
        plt.xlabel('Condition')
        
        # Place the legend outside the plot
        plt.legend(title='Classifier', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save each plot as a high-resolution 350 DPI PNG image
        plot_path = os.path.join(plot_output_dir, f'{metric}_box_plot.png')
        plt.savefig(plot_path, dpi=350, format='png', bbox_inches='tight')
        plt.close()

    print("Box plots saved for each metric with 350 DPI.")

if __name__ == "__main__":
    # Check if sufficient arguments are provided
    if len(sys.argv) != 5:
        print("Usage: python script.py <data_dir> <summary_output_path> <t_test_output_path> <plot_output_dir>")
        sys.exit(1)

    data_dir = sys.argv[1]
    summary_output_path = sys.argv[2]
    t_test_output_path = sys.argv[3]
    plot_output_dir = sys.argv[4]

    # Create plot output directory if it doesn't exist
    os.makedirs(plot_output_dir, exist_ok=True)

    main(data_dir, summary_output_path, t_test_output_path, plot_output_dir)
