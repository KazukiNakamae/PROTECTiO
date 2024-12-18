#!/usr/bin/env python3
import regex as re
import sys
import csv
import os

__authors__ = ["Kazuki Nakamae"]
__version__ = "1.0.0"

def get_cbe_substrate_20nt(cdna_seq, output_fn):
    def extract_context(text):
        # パターンの前後20文字を抜き出す正規表現
        patt = re.compile(r"[ATCG]{20}C[ATCG]{19}")
        return patt.findall(text, overlapped=True)

    text = cdna_seq.upper()
    results = extract_context(text)

    data = [{"sequence": result} for result in results]

    field_names = ["sequence"]
    with open(output_fn, "w") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=field_names, delimiter=',')
        # writer.writeheader()
        writer.writerows(data)

    sys.exit(0)

def print_usage():
    print(f"Usage: {sys.argv[0]} <cDNA sequence file> <output csv filename>")
    print("Options:")
    print("  -h, --help    Show this help message and exit")
    print("  -v, --version Show version information and exit")

def print_version():
    print(f"{sys.argv[0]} version {__version__}")
    print("Authors:", ", ".join(__authors__))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print_usage()
        sys.exit(0)
    
    if len(sys.argv) == 2 and sys.argv[1] in ("-v", "--version"):
        print_version()
        sys.exit(0)
    
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    cdna_file = sys.argv[1]
    output_fn = sys.argv[2]

    if not os.path.isfile(cdna_file):
        print(f"Error: The file {cdna_file} does not exist.")
        sys.exit(1)

    try:
        with open(cdna_file, 'r') as file:
            cdna_seq = file.read()
    except Exception as e:
        print(f"Error reading the file {cdna_file}: {e}")
        sys.exit(1)

    get_cbe_substrate_20nt(cdna_seq, output_fn)
