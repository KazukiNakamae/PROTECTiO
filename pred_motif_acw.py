#!/usr/bin/env python3

import sys
import csv

__authors__ = ["Kazuki Nakamae"]
__version__ = "1.1.0"

# Function to check if a given sequence matches the "ACW" motif
def matches_motif(subsequence):
    iupac_w = {'A', 'T'}
    return (subsequence[0] == 'A') and (subsequence[1] == 'C') and (subsequence[2] in iupac_w)

def main(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write the header to the output file
        writer.writerow(['flanking_sequence', 'pred'])

        # Process each row in the input file
        for row in reader:
            sequence = row[0]  # Assuming the DNA sequence is in the first column
            if len(sequence) >= 22:
                subsequence = sequence[19:22]  # Extract positions 20 to 22 (0-based indexing)
                label = 'LABEL_1' if matches_motif(subsequence) else 'LABEL_0'
            else:
                label = 'LABEL_0'  # Default to LABEL_0 if the sequence is too short

            writer.writerow([sequence, label])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py target.csv eval_res.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
