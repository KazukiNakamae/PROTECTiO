# PROTECTiO
PROTECTiO: Predicting RNA Off-target compared with Tissue-specific Expression for Classify Tissue and Organ

## Setup Environment

```bash
conda env create -f environment.yml
conda activate protectio
```

## Create a Database of Tissue-specific Transcript Expression

First, use `prep_PROTECTiO_db.sh` to extract transcripts with tissue-specific expression from [RefEx](https://refex.dbcls.jp)'s [RefEx_expression_RNAseq40_human_PRJEB2445.tsv.zip](https://refex.dbcls.jp/download/RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv.zip) and generate sequence datasets for classifier evaluation. By default, the generated dataset is evaluated with the [STL model](https://huggingface.co/KazukiNakamae/STLmodel) to assess CBE-based RNA off-targets. RNA off-target risk for each transcript is calculated as Effective Substrate Density (ESD) and saved in `density.csv`.

```bash
bash prep_PROTECTiO_db.sh -d "Human RNA-seq" -e "CBE" -O "<time stamp>_PROTECTiO_output"
rsync -av <time stamp>_PROTECTiO_output myPROTECTiO_db
```

To use other classifiers for evaluation and ESD calculation, use `add_custom_predictor_eval.sh`. The ESD values are saved as `<-p script name>_density.csv`.

```bash
# SNL model(https://huggingface.co/KazukiNakamae/SNLmodel)
bash add_custom_predictor_eval.sh -O myPROTECTiO_db -p pred_dnabert2_cbe_snv1.py

# ACW motif classifier
bash add_custom_predictor_eval.sh -O myPROTECTiO_db -p pred_motif_acw.py

# WCW motif classifier
bash add_custom_predictor_eval.sh -O myPROTECTiO_db -p pred_motif_wcw.py
```

Users can create their own evaluation scripts and integrate them into PROTECTiO by referencing the `pred_dnabert2_cbe_snv1.py` example.

## Aggregate Data by Tissue

Retrieve ESD values for transcripts associated with tissue-specific genes and perform aggregation and visualization for each tissue. Use the `--prefix` option to specify which classifier’s ESD values to use. If omitted, the default STL model ESD values are used.

```bash
# Default: STL model(https://huggingface.co/KazukiNakamae/STLmodel)
python aggregate_density_by_tissue.py \
  --refex_file myPROTECTiO_db/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir myPROTECTiO_db \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE

# SNL model(https://huggingface.co/KazukiNakamae/SNLmodel)
python aggregate_density_by_tissue.py \
  --refex_file myPROTECTiO_db/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir myPROTECTiO_db \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_snv1pred \
  --prefix pred_dnabert2_cbe_snv1_

# ACW motif
python aggregate_density_by_tissue.py \
  --refex_file myPROTECTiO_db/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir myPROTECTiO_db \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_acwpred \
  --prefix pred_motif_acw_

# WCW motif
python aggregate_density_by_tissue.py \
  --refex_file myPROTECTiO_db/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir myPROTECTiO_db \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_wcwpred \
  --prefix pred_motif_wcw_
```

## Comparative Plots and Statistical Testing

Comparisons of ESD values by tissue can be performed using `summary_density_by_tissue.py`.

```bash
# Default: STL model(https://huggingface.co/KazukiNakamae/STLmodel)
python summary_density_by_tissue.py \
  --input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE \
  --output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE

# SNL model(https://huggingface.co/KazukiNakamae/SNLmodel)
python summary_density_by_tissue.py \
  --input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_snv1pred \
  --output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE_snv1pred

# ACW motif
python summary_density_by_tissue.py \
  --input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_acwpred \
  --output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE_acwpred

# WCW motif
python summary_density_by_tissue.py \
  --input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_wcwpred \
  --output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE_wcwpred
```


We created the complete PROTECTiO Database ([PROTECTiO_db_v1_0_0](https://doi.org/10.6084/m9.figshare.28053845.v1)) using the four classifiers(ACW motif, WCW motif, STL model, SNL model). You can freely download it.

## (Supplementary) Use Classifier Prediction Functionality Only

Use `stand_alone_prediction.sh` to apply classifiers to custom FASTA or CSV files. Specify the classifier script with the `-p` option.

```bash
# ACW motif
bash stand_alone_prediction.sh \
  -O example/20241024_stand_alone_prediction_test_acw \
  -p pred_motif_acw.py \
  -t example/ENST00000288774_target_with_header.fasta \
  -i fasta

# WCW motif
bash stand_alone_prediction.sh \
  -O example/20241024_stand_alone_prediction_test_wcw \
  -p pred_motif_wcw.py \
  -t example/ENST00000288774_target_with_header.fasta \
  -i fasta

# STL model(https://huggingface.co/KazukiNakamae/STLmodel)
bash stand_alone_prediction.sh \
  -O example/20241024_stand_alone_prediction_test_cbe_sv1 \
  -p pred_dnabert2_cbe_sv1.py \
  -t example/ENST00000288774_target_with_header.fasta \
  -i fasta

# SNL model(https://huggingface.co/KazukiNakamae/SNLmodel)
bash stand_alone_prediction.sh \
  -O example/20241024_stand_alone_prediction_test_cbe_snv1 \
  -p pred_dnabert2_cbe_snv1.py \
  -t example/ENST00000288774_target_with_header.fasta \
  -i fasta
```


<details>
<summary>For Developers</summary>

# Setup environment
```bash
conda env create -f environment.yml;
conda activate protectio;
```

```bash
bash prep_PROTECTiO_db.sh -d "TEST RNA-seq" -e "CBE";
bash prep_PROTECTiO_db.sh -d "Human RNA-seq" -e "CBE" -O "20240910135922_PROTECTiO_output";
```
20240910135922_PROTECTiO_outputをPROTECTiO_db_v1_0_0/Human_RNA-seq_CBEとしてコピーしておく
```bash
rsync -av 20240910135922_PROTECTiO_output PROTECTiO_db_v1_0_0;
mv PROTECTiO_db_v1_0_0/20240910135922_PROTECTiO_output PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE;
diff -r -x ".*" 20240910135922_PROTECTiO_output PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE;
```
隠しファイル以外は同一ファイルであることを確認

他の予測モデル・モチーフ判定
```bash
mkdir PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended;
rsync -av PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE/* PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended/;
# DNABERT-2-CBE_Suzuki_Nakamae_v1
bash add_custom_predictor_eval.sh -O PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended -p pred_dnabert2_cbe_snv1.py;
# ACWモチーフベース評価
bash add_custom_predictor_eval.sh -O PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended -p pred_motif_acw.py;
# WCWモチーフベース評価
bash add_custom_predictor_eval.sh -O PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended -p pred_motif_wcw.py;
```

# 組織ごとにデータ集計

```bash
# DNABERT-2-CBE_Suzuki_v1
python aggregate_density_by_tissue.py \
  --refex_file PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE;

# DNABERT-2-CBE_Suzuki_Nakamae_v1
python aggregate_density_by_tissue.py \
  --refex_file PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_snv1pred \
  --prefix pred_dnabert2_cbe_snv1_;

# ACWモチーフ
python aggregate_density_by_tissue.py \
  --refex_file PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_acwpred \
  --prefix pred_motif_acw_;

# WCWモチーフ
python aggregate_density_by_tissue.py \
  --refex_file PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended/refex_db/fltr_RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv \
  --base_dir PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE_extended \
  --output_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_wcwpred \
  --prefix pred_motif_wcw_;
```

# 比較プロット・検定

```bash
# DNABERT-2-CBE_Suzuki_v1
python summary_density_by_tissue.py \
--input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE \
--output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE;

# DNABERT-2-CBE_Suzuki_Nakamae_v1
python summary_density_by_tissue.py \
--input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_snv1pred \
--output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE_snv1pred;

# ACWモチーフ
python summary_density_by_tissue.py \
--input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_acwpred \
--output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE_acwpred;

# WCWモチーフ
python summary_density_by_tissue.py \
--input_dir aggregated_ESD_v1_0_0_Human_RNA-seq_CBE_wcwpred \
--output_dir summary_ESD_v1_0_0_Human_RNA-seq_CBE_wcwpred;

v30_colon_Effective substrate density_upper_outliers_for_metascape.csv

metascape
Pathway & Process Enrichment
Biological Process (GO)
Cellular Component (GO)
Molecular Function (GO)
Min Overlap:3
P Value Cutoff:0.01
Min Enrichment:1.5
Protein-protein Interaction Enrichment
Skip

ShinyGO 0.81
Biological Process (GO)
FDR cutoff: 0.05
pathway size Min. 2 and Max. 2000
Remove redundancy: ON
Abbreviate pathways: ON
Show pathway IDs: ON
Font Size: 8
Aspect Ratio: 3

```

# 予測機能のみ利用
```bash
bash stand_alone_prediction.sh \
-O example/20241024_stand_alone_prediction_test_acw \
-p pred_motif_acw.py \
-t example/ENST00000288774_target_with_header.fasta \
-i fasta;

bash stand_alone_prediction.sh \
-O example/20241024_stand_alone_prediction_test_wcw \
-p pred_motif_wcw.py \
-t example/ENST00000288774_target_with_header.fasta \
-i fasta;

bash stand_alone_prediction.sh \
-O example/20241024_stand_alone_prediction_test_cbe_sv1 \
-p pred_dnabert2_cbe_sv1.py \
-t example/ENST00000288774_target_with_header.fasta \
-i fasta;

bash stand_alone_prediction.sh \
-O example/20241024_stand_alone_prediction_test_cbe_snv1 \
-p pred_dnabert2_cbe_snv1.py \
-t example/ENST00000288774_target_with_header.fasta \
-i fasta;
```

# 予測機能のみのDockerイメージの作成（ローカル利用） * ローカル側でドライバーが必要になるのであまり実用的ではない。MacOSでは厳しい。
```bash
sudo docker build -t kazukinakamae/protectio_prediction:v1.0.0 .;
```

# Dockerイメージによる予測
```bash
docker run --gpus all -v $PWD:/app/DATA --rm kazukinakamae/protectio_prediction:v1.0.0 bash stand_alone_prediction.sh \
    -O /app/DATA/example/20241024_stand_alone_prediction_test_acw_docker \
    -p pred_motif_acw.py \
    -t /app/DATA/example/ENST00000288774_target_with_header.fasta \
    -i fasta;

docker run --gpus all -v $PWD:/app/DATA --rm kazukinakamae/protectio_prediction:v1.0.0 bash stand_alone_prediction.sh \
    -O /app/DATA/example/20241024_stand_alone_prediction_test_wcw_docker \
    -p pred_motif_wcw.py \
    -t /app/DATA/example/ENST00000288774_target_with_header.fasta \
    -i fasta;

docker run --gpus all -v $PWD:/app/DATA --rm kazukinakamae/protectio_prediction:v1.0.0 bash stand_alone_prediction.sh \
    -O /app/DATA/example/20241024_stand_alone_prediction_test_cbe_sv1_docker \
    -p pred_dnabert2_cbe_sv1.py \
    -t /app/DATA/example/ENST00000288774_target_with_header.fasta \
    -i fasta;

docker run --gpus all -v $PWD:/app/DATA --rm kazukinakamae/protectio_prediction:v1.0.0 bash stand_alone_prediction.sh \
    -O /app/DATA/example/20241024_stand_alone_prediction_test_cbe_sv1_docker \
    -p pred_dnabert2_cbe_snv1.py \
    -t /app/DATA/example/ENST00000288774_target_with_header.fasta \
    -i fasta;
```















sudo du -hs 20240910135922_PROTECTiO_output | sort -h;
---
837M	20240910135922_PROTECTiO_output
---
sudo du -hs PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE | sort -h;
---
838M	PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE
---
diff -r -x ".*" 20240910135922_PROTECTiO_output PROTECTiO_db_v1_0_0/Human_RNA-seq_CBE;


20240910023554_PROTECTiO_output


# デバッグ

## モデルの確認
python pred_rna_offtarget_batch.py /Users/kazuki/GitHub/PROTECTiO/20240910015828_PROTECTiO_output/prediction_targets/NM_018087/ENST00000371429/target.csv ${PWD}/DNABERT-2-CBE_Suzuki_v1/ test.csv;

確認
python pred_rna_offtarget.py GGCAGGGCTGGGGAAGCTTACTGTGTCCAAGAGCCTGCTG ./DNABERT-2-CBE_Suzuki_v1/
# tensor([[-1.6488,  1.4636]])
# ['LABEL_1']
python pred_rna_offtarget.py GTCATCTAACAAAAATATTCCGTTGCAGGAAAAGCAAGCT ./DNABERT-2-CBE_Suzuki_v1/ # 訓練データ：Negativeが正解
# tensor([[ 0.5538, -0.5429]])
# ['LABEL_0']

pred_rna_offtarget_batch.py ./DNABERT-2-CBE_Suzuki_v1/

通常のDNABERTで出力させてみる
python pred_rna_offtarget.py GGCAGGGCTGGGGAAGCTTACTGTGTCCAAGAGCCTGCTGG zhihan1996/DNABERT-2-117M
# tensor([[ 0.0022, -0.0025]])
# ['LABEL_0']
python pred_rna_offtarget.py GTCATCTAACAAAAATATTCCGTTGCAGGAAAAGCAAGCTA zhihan1996/DNABERT-2-117M
# tensor([[-0.0788, -0.0239]])
# ['LABEL_1']
真逆の出力、Suzukiモデルはちゃんと機能している。


## 基質配列取得の確認

conda create -y -n test_env;
conda activate test_env;
conda install conda-forge::python=3.8 conda-forge::requests conda-forge::biopython;
### デバッグ
# BRCA1
python extract_codon_sequence_with_exons.py ENST00000357654 ./debug/20240909_check_extract_codon_sequence_with_exons/ENST00000357654;
17_43044295_43170327(ENST00000357654.9).dnaで確認
mRNA：ENST00000357654.9
対応するコンセンサスCDS：CCDS11453.1
-> 問題なし
# ENST00000445317（ncRNA）
python extract_codon_sequence_with_exons.py ENST00000445317 ./debug/20240909_check_extract_codon_sequence_with_exons/ENST00000445317;
Error: Unable to retrieve exon information for transcript ID ENST00000445317
エラーとして返す（ディレクトリ自体は生成されるが、target.csvは0バイトとなる）
# ISG15
python extract_codon_sequence_with_exons.py ENST00000649529 ./debug/20240909_check_extract_codon_sequence_with_exons/ENST00000649529;
mRNA：ENST00000649529.1
対応するコンセンサスCDS：CCDS6.1
-> 問題なし
# MRPL48
python extract_codon_sequence_with_exons.py ENST00000310614 ./debug/20240909_check_extract_codon_sequence_with_exons/ENST00000310614;
mRNA：ENST00000310614.12
対応するコンセンサスCDS：CCDS44676.1
-> 問題なし

tar -zcvf PROTECTiO_db_v1_0_0.tar.gz PROTECTiO_db_v1_0_0;
</details>