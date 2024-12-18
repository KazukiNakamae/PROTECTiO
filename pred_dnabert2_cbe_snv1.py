#!/usr/bin/env python3

import sys
import os
import csv
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

__authors__ = ["Kazuki Nakamae"]
__version__ = "1.1.0"

def pred_rna_offtarget_batch(dna_sequences, model_dir):
    """
    Predict RNA off-target effects from DNA sequences using a DNABERT-2 model.
    
    Args:
        dna_sequences (list): List of DNA sequences.
        model_dir (str): Directory containing the DNABERT-2 model.
    
    Returns:
        list: List of tuples containing the DNA sequence and its predicted label.
    """
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, trust_remote_code=True).to(device)
    except Exception as e:
        print(f"Error loading model from {model_dir}: {e}")
        sys.exit(1)

    inputs = tokenizer(dna_sequences, return_tensors='pt', padding=True, truncation=True)
    model.eval()
    with torch.no_grad():
        outputs = model(
            input_ids=inputs["input_ids"].to(device),
            attention_mask=inputs["attention_mask"].to(device),
        )
    
    y_preds = np.argmax(outputs.logits.cpu().detach().numpy(), axis=1)
    
    def id2label(x):
        return model.config.id2label[x]
    
    y_dash = [id2label(x) for x in y_preds]
    
    return list(zip(dna_sequences, y_dash))

def print_usage():
    print(f"Usage: {sys.argv[0]} <input DNA sequence file> <DNABERT-2 model directory> <output CSV file>")
    print("Options:")
    print("  -h, --help    Show this help message and exit")
    print("  -v, --version Show version information and exit")

def print_version():
    print(f"{sys.argv[0]} version {__version__}")
    print("Authors:", ", ".join(__authors__))

def save_to_csv(results, output_file):
    """
    Save the DNA sequence prediction results to a CSV file.

    Args:
        results (list): List of tuples containing the DNA sequence and prediction label.
        output_file (str): Path to the output CSV file.
    """
    try:
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['flanking_sequence', 'pred'])
            writer.writerows(results)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        elif len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
            print_version()
            sys.exit(0)
        else:
            print_usage()
            sys.exit(1)

    dna_file = sys.argv[1]
    output_file = sys.argv[2]
    
    model_dir = "DNABERT-2-CBE_Suzuki_Nakamae_v1/"

    if not os.path.isfile(dna_file):
        print(f"Error: The file {dna_file} does not exist.")
        sys.exit(1)

    try:
        with open(dna_file, 'r') as file:
            dna_sequences = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error reading the file {dna_file}: {e}")
        sys.exit(1)

    results = pred_rna_offtarget_batch(dna_sequences, model_dir)

    save_to_csv(results, output_file)
