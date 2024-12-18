#!/bin/bash

# Version
version() {
    echo "
prep_PROTECTiO_db.sh version beta 1
" >&2
}

# Help
usage() {
    echo "
usage: 
    $0 [OPTION]
    -d  RefEx database type: 
      Choose an item in the below list.
        Human GeneChip
        Human RNA-seq
        Mouse GeneChip
        Rat GeneChip
    -e  Editor type:
      Choose an item in the below list.
        CBE
        ABE

    optional arguments:
    -O Output directory (default: <Time_Stamp>_PROTECTiO_output)
    -h  Display this help and exit
    -v  Output version information and exit
" >&2
}

# Function
# 並列実行用のコマンド
extract_codon_sequences() {
  original_id=$1
  ensembl_transcript_id=$2
  arg_output_dir_name=$3
  arg_editor=$4
  arg_cnt=$5

  echo "${arg_cnt}: Original ID: ${original_id}, Ensembl transcript ID: ${ensembl_transcript_id}"

  # 既に処理済みか確認
  pred_target_fn="${arg_output_dir_name}/prediction_targets/${original_id}/${ensembl_transcript_id}/target.csv"
  if [ -f "${pred_target_fn}" ]; then
    if [ -s "${pred_target_fn}" ]; then
      echo "Target file ${pred_target_fn} already exists. Skipping."
      return 0
    fi
  fi

  # echo "Extract potential substrate sequences from ${ensembl_transcript_id}..."
  mkdir -p "${arg_output_dir_name}/prediction_targets/${original_id}/${ensembl_transcript_id}"

  if [ "${arg_editor}" = "CBE" ]; then
    # echo "Search CAA/CAG/CGA in CCDS sequences of ${ensembl_transcript_id}";
    python extract_codon_sequence_with_exons.py "${ensembl_transcript_id}" "${arg_output_dir_name}/prediction_targets/${original_id}/${ensembl_transcript_id}"
    sleep 0.072
    # REST API is rate-limited at 55,000 requests per hour. 
    # We set interval so that the 50,000 (<55,000) sequences can be downloaded per hour.
    # Maximum sequence that can be downloaded within 1 sec: 50,000/60/60 = 13.88888889 [sequences]
    # 1[sec] / 13.88888889 = 0.072
    # CBE substrate: NNNNNNNNNNNNNNNNNNNNCNNNNNNNNNNNNNNNNNNN
  else
    # echo "The ${arg_editor} is not allowed as the input. Aborting."
    return 1
  fi
}

# Export Function
export -f extract_codon_sequences

# Initialize
arg_database=""
arg_editor=""
arg_output_dir_name=$(date "+%Y%m%d%H%M%S")"_PROTECTiO_output"

# Get Options
while getopts d:e:O:hv OPT; do
    case $OPT in
    d) 
        arg_database="${OPTARG}"
        ;;
    e) 
        arg_editor="${OPTARG}"
        ;;
    O) 
        arg_output_dir_name="${OPTARG}"
        ;;
    h) 
        usage ; exit 0
        ;;
    v) 
        version ; exit 0
        ;;
    \?)
        usage ; exit 1
        ;;
    esac
done
shift $((OPTIND - 1))

if [ "${arg_database}" = "Mouse GeneChip" ] || [ "${arg_database}" = "Rat GeneChip" ]; then
  echo "Sorry... The ${arg_database} option has not yet been implemented. Please wait for a while."
  echo "prep_PROTECTiO_db.sh aborts..."
  exit 1;
elif [ "${arg_database}" = "Human GeneChip" ]; then
  echo "Use ${arg_database} RefEx Database..."
elif [ "${arg_database}" = "Human RNA-seq" ]; then
  echo "Use ${arg_database} RefEx Database..."
elif [ "${arg_database}" = "TEST GeneChip" ]; then
  echo "Use Dummy RefEx Database..."
elif [ "${arg_database}" = "TEST RNA-seq" ]; then
  echo "Use Dummy RefEx Database..."
else
  echo "The ${arg_database} is not allowed as the input. Please check the below help"
  usage
  echo "prep_PROTECTiO_db.sh aborts..."
  exit 1;
fi

if [ "${arg_editor}" = "ABE" ]; then
  echo "Sorry... The ${arg_editor} option has not yet been implemented. Please wait for a while."
  echo "prep_PROTECTiO_db.sh aborts..."
  exit 1;
elif [ "${arg_editor}" = "CBE" ]; then
  echo "Use ${arg_editor} Prediction Model..."
else
  echo "The ${arg_editor} is not allowed as the input. Please check the below help"
  usage
  echo "prep_PROTECTiO_db.sh aborts..."
  exit 1;
fi

echo "Make output folder: ${arg_output_dir_name}"
if [ ! -d "${arg_output_dir_name}" ]; then
  mkdir "${arg_output_dir_name}"
fi

echo "---------------------------------------------------------------------"
echo "|                  Download RefEx databases                         |"
echo "---------------------------------------------------------------------"
echo "Download RefEx database"
# Download RefEx database
if [ ! -d "${arg_output_dir_name}/refex_db" ]; then
  mkdir "${arg_output_dir_name}/refex_db";
fi
if [ "${arg_database}" = "Human GeneChip" ]; then
  # RefEx_tissue_specific_genechip_human_GSE7307.tsv.zip
  db_data="RefEx_tissue_specific_genechip_human_GSE7307.tsv";
  if [ -f "${arg_output_dir_name}/refex_db/${db_data}.zip" ]; then
    echo "${db_data} already exists. Skipping."
  else
    wget -P "${arg_output_dir_name}/refex_db" https://refex.dbcls.jp/download/RefEx_tissue_specific_genechip_human_GSE7307.tsv.zip;
  fi
elif [ "${arg_database}" = "Human RNA-seq" ]; then
  # RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv.zip
  db_data="RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv";
  if [ -f "${arg_output_dir_name}/refex_db/${db_data}.zip" ]; then
    echo "${db_data} already exists. Skipping."
  else
    wget -P "${arg_output_dir_name}/refex_db" https://refex.dbcls.jp/download/RefEx_tissue_specific_RNAseq_human_PRJEB2445.tsv.zip;
  fi
elif [ "${arg_database}" = "Mouse GeneChip" ]; then
  # RefEx_tissue_specific_genechip_mouse_GSE10246.tsv.zip
  db_data="RefEx_tissue_specific_genechip_mouse_GSE10246.tsv";
  if [ -f "${arg_output_dir_name}/refex_db/${db_data}.zip" ]; then
    echo "${db_data} already exists. Skipping."
  else
    wget -P "${arg_output_dir_name}/refex_db" https://refex.dbcls.jp/download/mRefEx_tissue_specific_genechip_mouse_GSE10246.tsv.zip;
  fi
elif [ "${arg_database}" = "Rat GeneChip" ]; then
  # RefEx_tissue_specific_genechip_rat_GSE952.tsv.zip
  db_data="RefEx_tissue_specific_genechip_rat_GSE952.tsv";
  if [ -f "${arg_output_dir_name}/refex_db/${db_data}.zip" ]; then
    echo "${db_data} already exists. Skipping."
  else
    wget -P "${arg_output_dir_name}/refex_db" https://refex.dbcls.jp/download/RefEx_tissue_specific_genechip_rat_GSE952.tsv.zip;
  fi
elif [ "${arg_database}" = "TEST GeneChip" ]; then
  db_data="RefEx_genechip_dummy.tsv";
  if [ -f "${arg_output_dir_name}/refex_db/${db_data}.zip" ]; then
    echo "${db_data} already exists. Skipping."
  else
    cp "test/RefEx_genechip_dummy.tsv.zip" "${arg_output_dir_name}/refex_db/RefEx_genechip_dummy.tsv.zip";
  fi
elif [ "${arg_database}" = "TEST RNA-seq" ]; then
  db_data="RefEx_rnaseq_dummy.tsv";
  if [ -f "${arg_output_dir_name}/refex_db/${db_data}.zip" ]; then
    echo "${db_data} already exists. Skipping."
  else
    cp "test/RefEx_rnaseq_dummy.tsv.zip" "${arg_output_dir_name}/refex_db/RefEx_rnaseq_dummy.tsv.zip";
  fi
else
  echo "Unexpected Error.";
  echo "Please contact the developers: kazukinakamae<at_mark>gmail.com";
  exit 1;
fi

if [ ! -f "${arg_output_dir_name}/refex_db/${db_data}" ]; then
  echo "Uncompress ${db_data}.zip...";
  unzip "${arg_output_dir_name}/refex_db/${db_data}.zip" -d "${arg_output_dir_name}/refex_db";
fi

echo "All transcripts:"
awk 'NR>1' "${arg_output_dir_name}/refex_db/${db_data}" | wc -l;
echo "Filtered ${db_data}...";
fltr_db_data="fltr_${db_data}"
if [ -f "${arg_output_dir_name}/refex_db/${fltr_db_data}" ]; then
  echo "${fltr_db_data} already exists. Skipping."
else
  awk -F'\t' 'NR==1 {print; next} {for(i=3; i<=NF; i++) if($i == 1 || $i == -1) {print; break}}' \
  "${arg_output_dir_name}/refex_db/${db_data}" \
  > "${arg_output_dir_name}/refex_db/${fltr_db_data}";
fi
echo "Over-expressed/Under-expressed transcripts in a tissue:"
awk 'NR>1' "${arg_output_dir_name}/refex_db/${fltr_db_data}" | wc -l;

echo "---------------------------------------------------------------------"
echo "|                  Retrieve Ensembl ID using Togo ID                |"
echo "---------------------------------------------------------------------"

echo "Access TogoID..."
if [ "${arg_database}" = "Human GeneChip" ]; then
  id_reference_json="${arg_output_dir_name}/affyprobe_enst.json"
  if [ -f "${id_reference_json}" ]; then
    echo "${id_reference_json} already exists. Skipping."
  else
    python ./affy2ensg.py "${arg_output_dir_name}/refex_db/${fltr_db_data}" "${arg_output_dir_name}/affyprobe_enst.json"
  fi
elif [ "${arg_database}" = "Human RNA-seq" ]; then
  id_reference_json="${arg_output_dir_name}/refseq_enst.json"
  if [ -f "${id_reference_json}" ]; then
    echo "${id_reference_json} already exists. Skipping."
  else
    python ./refseq2ensg.py "${arg_output_dir_name}/refex_db/${fltr_db_data}" "${arg_output_dir_name}/refseq_enst.json"
  fi
elif [ "${arg_database}" = "Mouse GeneChip" ]; then
  id_reference_json="${arg_output_dir_name}/affyprobe_enst.json"
  if [ -f "${id_reference_json}" ]; then
    echo "${id_reference_json} already exists. Skipping."
  else
    python ./affy2ensg.py "${arg_output_dir_name}/refex_db/${fltr_db_data}" "${arg_output_dir_name}/affyprobe_enst.json"
  fi
elif [ "${arg_database}" = "Rat GeneChip" ]; then
  id_reference_json="${arg_output_dir_name}/affyprobe_enst.json"
  if [ -f "${id_reference_json}" ]; then
    echo "${id_reference_json} already exists. Skipping."
  else
    python ./affy2ensg.py "${arg_output_dir_name}/refex_db/${fltr_db_data}" "${arg_output_dir_name}/affyprobe_enst.json"
  fi
elif [ "${arg_database}" = "TEST GeneChip" ]; then
  id_reference_json="${arg_output_dir_name}/affyprobe_enst.json"
  if [ -f "${id_reference_json}" ]; then
    echo "${id_reference_json} already exists. Skipping."
  else
    python ./affy2ensg.py "${arg_output_dir_name}/refex_db/${fltr_db_data}" "${arg_output_dir_name}/affyprobe_enst.json"
  fi
elif [ "${arg_database}" = "TEST RNA-seq" ]; then
  id_reference_json="${arg_output_dir_name}/refseq_enst.json"
  if [ -f "${id_reference_json}" ]; then
    echo "${id_reference_json} already exists. Skipping."
  else
    python ./refseq2ensg.py "${arg_output_dir_name}/refex_db/${fltr_db_data}" "${arg_output_dir_name}/refseq_enst.json"
  fi
else
  echo "Unexpected Error.";
  echo "Please contact the developers: kazukinakamae<at_mark>gmail.com";
  exit 1;
fi
echo "Complete downloading Ensembl ID list"

echo "----------------------------------------------------------------------------------"
echo "|                  Prepare substrate sequence from transcripts                   |"
echo "----------------------------------------------------------------------------------"

mkdir "${arg_output_dir_name}/prediction_targets"
# 全体の要素数を取得
total_id_cnt=$(jq -c '.[] | .results[]' "${id_reference_json}" | wc -l | xargs);
echo "*********************************";
echo "Search in ${total_id_cnt} using GNU Parallel"
# カウンター
id_counter=0;
jq -c '.[] | .results[]' "${id_reference_json}" | while read -r result; do
    id_counter=$((id_counter + 1))
    original_id=$(echo "$result" | jq -r '.[0]')
    ensembl_transcript_id=$(echo "$result" | jq -r '.[1]')
    echo "$original_id $ensembl_transcript_id $arg_output_dir_name $arg_editor ${id_counter}/${total_id_cnt}"
done | parallel --colsep ' ' -j 12 extract_codon_sequences {1} {2} {3} {4} {5};
echo "*********************************";

echo "----------------------------------------------------------------------------------"
echo "|                  Predict RNA-offtargeting in transcripts                       |"
echo "----------------------------------------------------------------------------------"

# prediction target filepath
target_files=$(find "${arg_output_dir_name}/prediction_targets" -type f -name "target.csv")
# 全体の要素数を取得
total_eval_target_num=$(echo "$target_files" | wc -l | xargs)
# カウンター
eval_target_counter=0;
# CSV header
# header="Sequence,Label"
if [ "${arg_editor}" = "ABE" ]; then
  echo "Sorry... The ${arg_editor} option has not yet been implemented. Please wait for a while."
  echo "prep_PROTECTiO_db.sh aborts..."
  exit 1;
elif [ "${arg_editor}" = "CBE" ]; then
  for dna_fasta in ${target_files}; do
      echo ""
      eval_target_counter=$((eval_target_counter + 1))
      # prediction target file
      echo "${eval_target_counter}/${total_eval_target_num} Target file: ${dna_fasta}";
      # prediction result file
      eval_res="$(dirname ${dna_fasta})/eval_res.csv";
      if [ ! -f "${eval_res}" ]; then
        if [ -s "${dna_fasta}" ]; then
          python pred_rna_offtarget_batch.py "${dna_fasta}" "${PWD}/DNABERT-2-CBE_Suzuki_v1/" "${eval_res}";
        else
          echo "The ${dna_fasta} is empty. Skipping processing.";
        fi
      else
        echo "${eval_res} already exists. Skipping.";
      fi
      # Calculate effective substrate density (effective C substrate / all C substrate / transcript length )
      if [ ! -f "$(dirname ${dna_fasta})/density.csv" ]; then
        if [ -f "${eval_res}" ]; then
          python calc_eff_substrate_density.py \
          -e "${eval_res}" \
          -t "$(dirname ${dna_fasta})/table.csv" \
          -d "$(dirname ${dna_fasta})/density.csv";
        fi
      fi
  done;
else
  echo "The ${arg_editor} is not allowed as the input. Please check the below help"
  usage
  echo "prep_PROTECTiO_db.sh aborts..."
  exit 1;
fi

echo "--------------------------------------------------------------"
echo "All processes were successfully done!"
echo "--------------------------------------------------------------"
exit 0;
