#!/bin/bash

# New Shell Script: replace_prediction_script.sh
# Overview:
#   - Replaces 'pred_rna_offtarget_batch.py' with a Python script specified by a command-line argument.
#   - Saves the results to <Output directory>/$(dirname ${target_file})/xxx_eval_res.csv.
#   - Allows specifying 'arg_output_dir_name', and 'python_script' via command-line arguments.

# Initialize variables
arg_output_dir_name=""
python_script=""

# Display help message
usage() {
    echo "Usage: $0 -O <output_directory> -p <python_script> [-e <editor_type>]"
    echo "  -O Specify the output directory."
    echo "  -p Specify the Python script to execute."
    echo "  -h Display this help message."
}

# Parse command-line arguments
while getopts "O:p:h" opt; do
  case $opt in
    O)
      arg_output_dir_name="${OPTARG}"
      ;;
    p)
      python_script="${OPTARG}"
      ;;
    h)
      usage
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      exit 1
      ;;
  esac
done

# Check if the output directory and Python script are specified
if [ -z "${arg_output_dir_name}" ] || [ -z "${python_script}" ]; then
  echo "Error: Please specify the output directory with -O and the Python script with -p." >&2
  usage
  exit 1
fi

# Check if the specified Python script exists and is executable
if [ ! -f "${python_script}" ]; then
  echo "Error: The specified Python script '${python_script}' does not exist." >&2
  exit 1
fi

# Get the list of target files
target_files=$(find "${arg_output_dir_name}/prediction_targets" -type f -name "target.csv")

# Get the total number of targets
total_eval_target_num=$(echo "$target_files" | wc -l | xargs)
eval_target_counter=0

echo "----------------------------------------------------------------------------------"
echo "|                  Predict RNA off-targeting in transcripts                      |"
echo "----------------------------------------------------------------------------------"

for target_file in ${target_files}; do
    echo ""
    eval_target_counter=$((eval_target_counter + 1))
    echo "${eval_target_counter}/${total_eval_target_num} Target file: ${target_file}"

    # Set the path for the new result file
    eval_res="$(dirname "${target_file}")/${python_script%.*}_eval_res.csv"

    # Check if the result file already exists
    if [ ! -f "${eval_res}" ]; then
      if [ -s "${target_file}" ]; then
        # Execute the specified Python script
        python "${python_script}" "${target_file}" "${eval_res}"
      else
        echo "The file ${target_file} is empty. Skipping processing."
      fi
    else
      echo "${eval_res} already exists. Skipping."
    fi

    # Optionally calculate effective substrate density
    if [ ! -f "$(dirname "${target_file}")/${python_script%.*}_density.csv" ]; then
      if [ -f "${eval_res}" ]; then
        python calc_eff_substrate_density.py \
        -e "${eval_res}" \
        -t "$(dirname "${target_file}")/table.csv" \
        -d "$(dirname "${target_file}")/${python_script%.*}_density.csv"
      fi
    fi
done

echo "--------------------------------------------------------------"
echo "All processes were successfully done!"
echo "--------------------------------------------------------------"
exit 0
