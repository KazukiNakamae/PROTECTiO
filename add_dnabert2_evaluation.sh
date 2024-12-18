#!/bin/bash

# Help
usage() {
    echo "
usage: 
    $0 [OPTION]
    -O  Output directory (required)
    -e  Editor type (required): 
      Choose 'CBE'
    -m  Model directory (required): 
      Path to DNABERT-2-CBE model directory
    -l  Label
        prediction label
    -h  Display this help and exit
" >&2
}

# Initialize
arg_editor=""
arg_output_dir_name=""
arg_model_dir=""
arg_label=""

# Get Options
while getopts O:e:m:l:hv OPT; do
    case $OPT in
    O) 
        arg_output_dir_name="${OPTARG}"
        ;;
    e) 
        arg_editor="${OPTARG}"
        ;;
    m)
        arg_model_dir="${OPTARG}"
        ;;
    l)
        arg_label="${OPTARG}"
        ;;
    h) 
        usage ; exit 0
        ;;
    \?)
        usage ; exit 1
        ;;
    esac
done

# Check if output directory, editor, and model directory are provided
if [ -z "$arg_output_dir_name" ]; then
  echo "Output directory is required."
  usage
  exit 1
fi

if [ -z "$arg_editor" ]; then
  echo "Editor type is required."
  usage
  exit 1
fi

if [ -z "$arg_model_dir" ]; then
  echo "Model directory is required."
  usage
  exit 1
fi

if [ -z "$arg_label" ]; then
  echo "Prediction label is required."
  usage
  exit 1
fi

if [ "${arg_editor}" != "CBE" ]; then
  echo "Only CBE editor is supported for now."
  exit 1
fi

# Start the RNA-offtarget prediction process
echo "----------------------------------------------------------------------------------"
echo "|                  Predict RNA-offtargeting in transcripts                       |"
echo "----------------------------------------------------------------------------------"

# Find prediction target files
target_files=$(find "${arg_output_dir_name}/prediction_targets" -type f -name "target.csv")

# Count the number of target files
total_eval_target_num=$(echo "$target_files" | wc -l | xargs)
echo "Found ${total_eval_target_num} target files."

# Initialize counter
eval_target_counter=0

# Process each target file
for dna_fasta in ${target_files}; do
    eval_target_counter=$((eval_target_counter + 1))
    echo "Processing ${eval_target_counter}/${total_eval_target_num} Target file: ${dna_fasta}"
    
    # Define the paths for the new files
    eval_res="$(dirname ${dna_fasta})/${arg_label}_eval_res.csv"
    density_file="$(dirname ${dna_fasta})/${arg_label}_density.csv"
    table_file="$(dirname ${dna_fasta})/${arg_label}_table.csv"
    
    # Predict RNA offtargeting if eval_res doesn't exist
    if [ ! -f "${eval_res}" ]; then
        if [ -s "${dna_fasta}" ]; then
            echo "Running RNA-offtarget prediction for ${dna_fasta}"
            python pred_rna_offtarget_batch.py "${dna_fasta}" "${arg_model_dir}" "${eval_res}"
        else
            echo "The file ${dna_fasta} is empty. Skipping."
            continue
        fi
    else
        echo "${eval_res} already exists. Skipping."
    fi
    
    # Calculate effective substrate density and generate new density and table files
    if [ ! -f "${density_file}" ]; then
        if [ -f "${eval_res}" ]; then
            echo "Calculating effective substrate density and generating new files for ${dna_fasta}"
            python calc_eff_substrate_density.py \
            -e "${eval_res}" \
            -t "${table_file}" \
            -d "${density_file}"
        else
            echo "Evaluation results not found for ${dna_fasta}. Skipping density calculation."
        fi
    else
        echo "${density_file} already exists. Skipping."
    fi
done

echo "--------------------------------------------------------------"
echo "All RNA-offtarget prediction and file generation done!"
echo "--------------------------------------------------------------"
exit 0
