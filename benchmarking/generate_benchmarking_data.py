import os
import argparse
import re

# IUPACコードを正規表現に変換するための辞書を定義
IUPAC_CODES = {
    'A': 'A',
    'C': 'C',
    'G': 'G',
    'T': 'T',
    'R': '[AG]',
    'Y': '[CT]',
    'S': '[GC]',
    'W': '[AT]',
    'K': '[GT]',
    'M': '[AC]',
    'B': '[CGT]',
    'D': '[AGT]',
    'H': '[ACT]',
    'V': '[ACG]',
    'N': '[ACGT]'
}

def iupac_to_regex(motif):
    """IUPACモチーフを正規表現に変換"""
    return ''.join([IUPAC_CODES[base] for base in motif])

def read_fasta(file_path):
    sequences = []
    with open(file_path, "r") as file:
        sequence = ""
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                if sequence:
                    sequences.append(sequence)
                    sequence = ""
            else:
                sequence += line
        if sequence:
            sequences.append(sequence)
    return sequences

def remove_duplicates(seq_pos, seq_neg):
    print("Removing positive sequences that also exist in nagative sequences")
    return [item for item in seq_pos if item not in seq_neg]

def write_data(seq_list, out_fn):
    with open(out_fn, "w") as output_file:
        for seq in seq_list:
            output_file.write(seq + "\n")

def match_motif(seq_list, motif_regex, start_index, end_index):
    """モチーフをIUPACに基づいて照合する"""
    motif_seq = []
    non_motif_seq = []
    
    for seq in seq_list:
        subseq = seq[start_index:end_index]
        if re.search(motif_regex, subseq):  # re.matchからre.searchに変更
            motif_seq.append(seq)
        else:
            non_motif_seq.append(seq)
    
    return motif_seq, non_motif_seq

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some FASTA files.")
    parser.add_argument("--positive", type=str, required=True, help="Path to the positive FASTA file")
    parser.add_argument("--negative", type=str, required=True, help="Path to the negative FASTA file")
    parser.add_argument("--outdir", type=str, default=".", help="Output directory")
    parser.add_argument("--motif", type=str, required=True, help="Motif to search for in sequences")
    parser.add_argument("--start_pos", type=int, required=True, help="Position in the sequence to start matching the motif")
    args = parser.parse_args()

    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # メイン処理
    seq_pos = read_fasta(args.positive)
    seq_neg = read_fasta(args.negative)

    print(f"Sequences with positive label: {len(seq_pos)}")
    print(f"Sequences with negative label: {len(seq_neg)}")

    # Negativeデータセットにも存在している配列をPositiveデータセットから除外
    seq_pos = remove_duplicates(seq_pos, seq_neg)
    print(f"Filtered sequences with positive label: {len(seq_pos)}")

    # モチーフでフィルタリング
    motif_regex = iupac_to_regex(args.motif)
    start_index = int(args.start_pos) - 1
    end_index = start_index + len(args.motif)
    motif_seq_pos, non_motif_seq_pos = match_motif(seq_pos, motif_regex, start_index, end_index)
    motif_seq_neg, non_motif_seq_neg = match_motif(seq_neg, motif_regex, start_index, end_index)

    print(f"Motif matching sequences with positive label: {len(motif_seq_pos)}")
    print(f"Motif matching sequences with negative label: {len(motif_seq_neg)}")
    print(f"Non-motif matching sequences with positive label: {len(non_motif_seq_pos)}")
    print(f"Non-motif matching sequences with negative label: {len(non_motif_seq_neg)}")

    # rep<数字>の部分と後ろの文字列を抽出
    match = re.search(r"(.*)_rep(\d+)_.*", args.positive)
    condition = ""
    replication = ""
    if match:
        condition = match.group(1)
        replication = match.group(2)
    else:
        condition = ""
        replication = ""

    # ファイル出力
    write_data(motif_seq_pos, os.path.join(args.outdir, f"{args.motif}_motif_pos.txt"))
    write_data(non_motif_seq_pos, os.path.join(args.outdir, f"{args.motif}_non_motif_pos.txt"))
    write_data(motif_seq_neg, os.path.join(args.outdir, f"{args.motif}_motif_neg.txt"))
    write_data(non_motif_seq_neg, os.path.join(args.outdir, f"{args.motif}_non_motif_neg.txt"))
    
    with open(os.path.join(args.outdir, f"{args.motif}_motif_count.csv"), "w") as output_file:
        output_file.write(f"{condition},{replication},{len(motif_seq_pos)},{str(len(non_motif_seq_pos))}\n")
