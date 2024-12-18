#!/bin/bash

# Initialize variables
arg_output_dir_name=""
python_script=""
target_file=""
input_type=""
converted_file=""

# Display help message
usage() {
    echo "Usage: $0 -O <output_directory> -p <python_script> -t <target_file> -i <input_type> [-h]"
    echo "  -O Specify the output directory."
    echo "  -p Specify the Python script to execute."
    echo "  -t Specify the target file to process."
    echo "  -i Specify the input type (csv or fasta)."
    echo "  -h Display this help message."
}

# Parse command-line arguments
while getopts "O:p:t:i:h" opt; do
  case $opt in
    O)
      arg_output_dir_name="${OPTARG}"
      ;;
    p)
      python_script="${OPTARG}"
      ;;
    t)
      target_file="${OPTARG}"
      ;;
    i)
      input_type="${OPTARG}"
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

# Check if the required arguments are specified
if [ -z "${arg_output_dir_name}" ] || [ -z "${python_script}" ] || [ -z "${target_file}" ] || [ -z "${input_type}" ]; then
  echo "Error: Please specify the output directory with -O, the Python script with -p, the target file with -t, and the input type with -i." >&2
  usage
  exit 1
fi

echo "Make output folder: ${arg_output_dir_name}"
if [ ! -d "${arg_output_dir_name}" ]; then
  mkdir "${arg_output_dir_name}"
fi

# Check if the specified Python script exists
if [ ! -f "${python_script}" ]; then
  echo "Error: The specified Python script '${python_script}' does not exist." >&2
  exit 1
fi

# Function to convert FASTA to CSV
convert_fasta_to_csv() {
  fasta_file="$1"
  output_dir_name="$2"
  output_csv_file="${output_dir_name}/tmp.csv"
  
  echo "Converting FASTA file to CSV..."
  if [ -f "${fasta_file}" ]; then
    # Create CSV from FASTA (only keeping the sequence part)
    grep -v ^\> "${fasta_file}" > "${output_csv_file}"
    
    if [ -f "${output_csv_file}" ];then
      echo "Conversion complete: ${output_csv_file}"
    else
      echo "Error: Failed to convert FASTA to CSV." >&2
      exit 1
    fi
  else
    echo "Error: The specified FASTA file '${fasta_file}' does not exist." >&2
    exit 1
  fi
}

# Function to validate and convert the target file
validate_and_convert_target_file() {
  file="$1"
  output_dir_name="$2"
  target_file_name=$(basename "${file}")
  converted_file="${output_dir_name}/target.csv"

  echo "Validating and converting target file: ${file}..."

  # Read through each line and perform validation and conversion
  while IFS= read -r line; do
    # Convert to uppercase
    upper_line=$(echo "$line" | tr 'a-z' 'A-Z')

    # Check if the line has 40 characters and contains only A, T, C, G
    if [[ ! $upper_line =~ ^[ATCG]{40}$ ]]; then
      echo "Error: Invalid sequence found in file '${file}'. Each line must contain exactly 40 characters consisting of A, T, C, or G." >&2
      rm -f "${converted_file}"
      exit 1
    fi

    # Write the converted line to a new file
    echo "$upper_line" >> "$converted_file"
  done < "$file"

  echo "Converted file saved as: ${converted_file}"
}

# Process input based on input type
eval_file="${target_file}"
if [ "${input_type}" == "fasta" ]; then
  # Convert FASTA to CSV
  convert_fasta_to_csv "${target_file}" "${arg_output_dir_name}"
  eval_file="${arg_output_dir_name}/tmp.csv"
elif [ "${input_type}" != "csv" ]; then
  echo "Error: Unsupported input type '${input_type}'. Only 'csv' or 'fasta' are accepted." >&2
  exit 1
fi

# Check if the target file exists after potential conversion
if [ ! -f "${eval_file}" ]; then
  echo "Error: The specified target file '${eval_file}' does not exist." >&2
  exit 1
fi

# Validate and convert the target file to ensure each line is a 40 character long sequence of A, T, C, G
validate_and_convert_target_file "${eval_file}" "${arg_output_dir_name}"
converted_file="${output_dir_name}/target.csv"

echo "----------------------------------------------------------------------------------"
echo "|                  Predict RNA off-targeting in transcripts                      |"
echo "----------------------------------------------------------------------------------"

echo "Processing target file: ${converted_file}"

# Set the path for the new result file
eval_res="${arg_output_dir_name}/eval_res.csv"

# Check if the result file already exists
if [ ! -f "${eval_res}" ]; then
  if [ -s "${converted_file}" ]; then
    # Execute the specified Python script
    python "${python_script}" "${converted_file}" "${eval_res}"
  else
    echo "The file ${converted_file} is empty. Skipping processing."
  fi
else
  echo "${eval_res} already exists. Skipping."
fi

echo "Clean files"
rm "${arg_output_dir_name}/tmp.csv"

echo "--------------------------------------------------------------"
echo "All processes were successfully done!"
echo "--------------------------------------------------------------"
exit 0
