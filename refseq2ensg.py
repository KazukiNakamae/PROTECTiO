import pandas as pd
import requests
import json
import time
import sys

__authors__ = ["Kazuki Nakamae", "Takayuki Suzuki"]
__version__ = "1.0.0"

def affy2ensg(RefEx_db, output_fn):
    # read a tsv file and make a dataframe
    df = pd.read_csv(RefEx_db, sep='\t')
    # get the first column
    id_list = df.iloc[:, 0]
    # get the first column as a list
    id_list = df.iloc[:, 0].tolist()

    # API Request unit: 500 queries / 1 request
    id_split = [id_list[i : i + 500] for i in range(0, len(id_list), 500)]
    print(str(len(id_list)) + " Queries")
    print("Expectd time: "+str(len(id_split) * 0.5))

    print("[<NCBI RefSeq ID>, <Ensembl transcript ID>]")
    refseq_enst_list = []
    for i in id_split:
        input = ','.join(i)
        url = f'https://api.togoid.dbcls.jp/convert?ids={input}&route=refseq_rna,ensembl_transcript&report=all&format=json'
        r = requests.get(url)
        print(r.json()["results"])
        refseq_enst_list.append(r.json())
        time.sleep(0.5)

    # write out a json file
    with open(output_fn, 'w') as f:
        json.dump(refseq_enst_list, f, indent=4)

def print_usage():
    print(f"Usage: {sys.argv[0]} <RefEx database type> <output json filename>")
    print("Options:")
    print("  -h, --help    Show this help message and exit")
    print("  -v, --version Show version information and exit")

def print_version():
    print(f"{sys.argv[0]} version {__version__}")
    print("Authors:", ", ".join(__authors__))

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
    
    RefEx_db = sys.argv[1]
    output_fn = sys.argv[2]

    affy2ensg(RefEx_db, output_fn)