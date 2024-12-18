import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, matthews_corrcoef, confusion_matrix
import sys
import csv
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_metrics(pos_file, neg_file, output_path, condition, classifier, rep):
    # Load the positive and negative datasets
    df_pos = pd.read_csv(pos_file)
    df_neg = pd.read_csv(neg_file)

    # Assuming the actual labels for positive dataset are all 1 (positive) and for negative dataset are all 0 (negative)
    y_true_pos = [1] * len(df_pos)
    y_true_neg = [0] * len(df_neg)

    # Map 'LABEL_1' to 1 (positive) and 'LABEL_0' to 0 (negative) in the prediction column
    y_pred_pos = df_pos['pred'].map({'LABEL_1': 1, 'LABEL_0': 0}).values
    y_pred_neg = df_neg['pred'].map({'LABEL_1': 1, 'LABEL_0': 0}).values

    # Combine the true and predicted labels
    y_true = y_true_pos + y_true_neg
    y_pred = list(y_pred_pos) + list(y_pred_neg)

    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    mat_cor = matthews_corrcoef(y_true, y_pred)

    # Define output file names
    metrics_output_file = f'{output_path}/{condition}_{classifier}_{rep}_metrics_output.csv'
    cm_output_file = f'{output_path}/{condition}_{classifier}_{rep}_confusion_matrix.png'

    # Write metrics to a CSV file
    with open(metrics_output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['condition', 'classifier', 'rep', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'MCC'])
        # Write data row
        writer.writerow([condition, classifier, rep, accuracy, precision, recall, f1, mat_cor])

    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Plot confusion matrix as a heatmap with adjusted font size
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, 
                xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'], 
                annot_kws={"size": 20})  # Adjust font size here
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title(f'Confusion Matrix ({condition} - {classifier} - {rep})')
    
    # Save the confusion matrix as a PNG file
    plt.savefig(cm_output_file, dpi=350)
    plt.close()

    print(f'Metrics saved to {metrics_output_file}')
    print(f'Confusion matrix saved to {cm_output_file}')

if __name__ == '__main__':
    # Command-line arguments: pos_file, neg_file, output_path, condition, classifier, rep
    if len(sys.argv) != 7:
        print("Usage: python script.py <path_to_eval_res_pos.csv> <path_to_eval_res_neg.csv> <output_path> <condition> <classifier> <rep>")
        sys.exit(1)

    pos_file = sys.argv[1]
    neg_file = sys.argv[2]
    output_path = sys.argv[3]
    condition = sys.argv[4]
    classifier = sys.argv[5]
    rep = sys.argv[6]

    calculate_metrics(pos_file, neg_file, output_path, condition, classifier, rep)
