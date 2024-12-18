import requests
from Bio.Seq import Seq
from Bio.Data import CodonTable
import argparse
import sys
import os

# 標準的なコドン表を取得
codon_table = CodonTable.unambiguous_dna_by_id[1]

def get_exon_info(transcript_id):
    """Ensembl APIを使って指定されたトランスクリプトIDのエクソン情報を取得する"""
    url = f"https://rest.ensembl.org/map/cds/{transcript_id}/1..99999999?content-type=application/json"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Unable to retrieve exon information for transcript ID {transcript_id}")
        sys.exit(1)

    exon_data = response.json()

    if not exon_data['mappings']:
        print(f"Error: No exon data found for transcript ID {transcript_id}")
        sys.exit(1)
    
    return exon_data['mappings']

def get_genomic_sequence(region):
    """指定されたゲノム領域（例: 1:1000..2000:1）から配列を取得する"""
    url = f"https://rest.ensembl.org/sequence/region/human/{region}?content-type=application/json"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Unable to retrieve sequence for region {region}")
        sys.exit(1)
    return response.json()['seq']

def extract_cds_from_exons(exon_data, log_file):
    """エクソン情報をもとにゲノム配列からCDS配列を構築する"""
    strand = exon_data[0]['strand']
    sorted_exons = sorted(exon_data, key=lambda x: x['start'], reverse=(strand == -1))

    cds_sequence = ""
    exon_regions = []

    exon_number = 0
    for exon in sorted_exons:
        chrom = exon['seq_region_name']
        start = exon['start']
        end = exon['end']
        exon_number += 1
        
        region = f"{chrom}:{start}..{end}:{strand}"
        exon_sequence = get_genomic_sequence(region)
        exon_regions.append((chrom, start, end, strand))

        # エクソン座標と配列をログに書き込む
        log_file.write(f"\nExon {exon_number} coordinates: {region}\n")
        log_file.write(f"Exon {exon_number} sequence: {exon_sequence}\n")
        
        cds_sequence += exon_sequence
    
    return cds_sequence, exon_regions

def map_residue_to_genomic_position(residue_position, exon_regions):
    """アミノ酸の位置をエクソンのゲノム座標にマッピングする"""
    codon_start_in_cds = residue_position * 3
    current_cds_position = 0

    for chrom, start, end, strand in exon_regions:
        exon_length = end - start + 1
        if current_cds_position + exon_length >= codon_start_in_cds + 3:
            codon_start_in_exon = codon_start_in_cds - current_cds_position
            genomic_start = start + codon_start_in_exon
            genomic_end = genomic_start + 2  # コドンは3塩基

            if strand == -1:
                genomic_start, genomic_end = end - codon_start_in_exon - 2, end - codon_start_in_exon
            
            return chrom, genomic_start, genomic_end, strand

        current_cds_position += exon_length

    raise ValueError("Residue position out of range for the provided exon regions")

def get_flanking_sequence(chrom, codon_start, codon, strand):
    """指定されたゲノム領域の前後20ntの配列を取得し、左から数えて21番目にコドン内のCが来るように調整"""
    c_position_in_codon = codon.find('C')
    
    if c_position_in_codon == -1:
        return None

    if strand == 1:
        c_position_in_genome = codon_start + c_position_in_codon
        flanking_start = max(1, c_position_in_genome - 20)
        flanking_end = c_position_in_genome + 19
    elif strand == -1:
        c_position_in_genome = codon_start + c_position_in_codon + 2
        flanking_start = max(1, c_position_in_genome - 19)
        flanking_end = c_position_in_genome + 20
    
    region = f"{chrom}:{flanking_start}..{flanking_end}:{strand}"
    flanking_sequence = get_genomic_sequence(region)

    return flanking_sequence

def codon_changes_amino_acid(codon, onlystop=False):
    """C→T変換によってアミノ酸が変わるかどうかを確認する"""
    if not onlystop:
      original_amino_acid = codon_table.forward_table.get(codon, 'X')
      mutated_codon = codon.replace('C', 'T')
      mutated_amino_acid = codon_table.forward_table.get(mutated_codon, 'X')
      return original_amino_acid != mutated_amino_acid
    else:
      return (codon in ["CAA", "CAG", "CGA"])

def main():
    parser = argparse.ArgumentParser(description='Extract codon and surrounding sequence for residues where C->T mutation affects amino acid.')
    parser.add_argument('transcript_id', type=str, help='Ensembl Transcript ID (e.g., ENST00000357654)')
    parser.add_argument('output_dir', type=str, help='Output directory for result files')
    
    args = parser.parse_args()

    # ディレクトリ作成
    os.makedirs(args.output_dir, exist_ok=True)

    # ファイルハンドルを開く
    log_file = open(os.path.join(args.output_dir, "log.txt"), "w")
    flanking_file = open(os.path.join(args.output_dir, "target.csv"), "w")
    table_file = open(os.path.join(args.output_dir, "table.csv"), "w")

    # ヘッダを書き込む
    table_file.write("flanking_sequence,amino_acid,codon,pos,amino_acid_len,rel_amino_acid_pos\n")

    # エクソン情報を取得
    exon_data = get_exon_info(args.transcript_id)

    # ゲノム配列からエクソン情報を基にCDS配列を構築
    cds_sequence, exon_regions = extract_cds_from_exons(exon_data, log_file)

    # CDS配列を翻訳してアミノ酸配列を確認
    log_file.write(f"Merged CDS sequence: {cds_sequence}\n")
    cds_seq_obj = Seq(cds_sequence)
    amino_acid_sequence = cds_seq_obj.translate(to_stop=True)

    log_file.write(f"\nSearching for residues where C->T mutation affects the amino acid...\n")

    amino_acid_len = len(amino_acid_sequence)
    for pos in range(amino_acid_len):
        codon_start = pos * 3
        codon = cds_sequence[codon_start:codon_start + 3]

        if 'C' in codon and codon_changes_amino_acid(codon, onlystop=True):
            log_file.write(f"\nResidue at position {int(pos + 1)} ({amino_acid_sequence[pos]}) with codon {codon} is affected by C->T mutation:\n")

            chrom, genomic_start, genomic_end, strand = map_residue_to_genomic_position(pos, exon_regions)

            flanking_sequence = get_flanking_sequence(chrom, genomic_start, codon, strand)
            
            if flanking_sequence:
                log_file.write(f"Genomic coordinates for substrate sequence: {chrom}:{genomic_start}..{genomic_end} (strand: {strand})\n")
                log_file.write(f"Genomic sequence for substrate sequence: {flanking_sequence}\n")

                flanking_file.write(f"{flanking_sequence}\n")

                rel_amino_acid_pos = round(float(pos / amino_acid_len), 5)
                log_file.write(f"Relative amino acid position [0-1]: {rel_amino_acid_pos}\n")

                table_file.write(f"{flanking_sequence},{amino_acid_sequence[pos]},{codon},{pos},{amino_acid_len},{rel_amino_acid_pos}\n")

    log_file.close()
    flanking_file.close()
    table_file.close()

if __name__ == "__main__":
    main()
