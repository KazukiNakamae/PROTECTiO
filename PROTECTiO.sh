# Version
version() {
    echo "
PROTECTiO version beta 1: 
" >&2
}

# Help
usage() {
    echo "
usage: 
    $0 [OPTION]
    -d  RefEx database type: 
      Choose an item in the below list.
        Human
        Mouse
        Rat
    -t  Target tissue and organ type: 
      Choose an item in the below list.
        adipose
        adrenal_gland
        artery_and_aorta
        bladder
        bone
        bone_marrow
        brain_stem
        breast
        cerebellum
        cerebrum
        colon
        corpus_callosum_and_glia
        esophagus
        eye
        heart
        intestine
        kidney
        liver_and_hepato
        lung
        lymphnode
        muscle
        ovary
        pancreas
        peripheral_blood
        peripheral_nerve
        pineal_gland
        pituitary
        placenta
        prostate
        retina
        salivary
        skin
        spine
        spleen
        stomach
        testis
        thymus
        thyroid_and_parathyroid
        uterus
        vein
    -e  Editor type:
      Choose an item in the below list.
        CBE
        ABE

    optional arguments:
    -O Output directiory (defalut: <Time_Stamp>_PROTECTiO_output)
    -h  Display this help and exit
    -v  Output version information and exit
" >&2
}

# Initialize
arg_database=""
arg_tissue=""
arg_editor=""
arg_outpur_dir_name=`date "+%Y%m%d%H%M%S"`"_PROTECTiO_output"

# Get Options
while getopts d:t:e:Ohv OPT; do
    case $OPT in
    d) 
        arg_database="${OPTARG}"
        ;;
    t) 
        arg_tissue="${OPTARG}"
        ;;
    e) 
        arg_editor="${OPTARG}"
        ;;
    O) 
        arg_outpur_dir_name="${OPTARG}"
        ;;
    h) 
        usage ; exit 0
        ;;
    v) 
        version ; exit 0
        ;;
    esac
done
shift $((OPTIND - 1))

if [ ${arg_database} = "Mouse" ] || [ ${arg_database} = "Rat" ]; then
  echo "Sorry... The "${arg_database}" option has not yet been implemented. Please wait for a while."
  echo "PROTECTiO.sh aborts..."
  exit 1;
elif [ ${arg_database} = "Human" ] ]; then
  echo "Use "${arg_database}" RefEx Database..."
else
  echo "The "${arg_database}" is not allowed as the input. Please check the below help"
  usage
  echo "PROTECTiO.sh aborts..."
  exit 1;
fi

tissue_label=""
if [ ${arg_tissue} = "cerebrum" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v1_cerebrum";
elif [ ${arg_tissue} = "cerebellum" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v2_cerebellum";
elif [ ${arg_tissue} = "brain_stem" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v3_brain_stem";
elif [ ${arg_tissue} = "corpus_callosum_and_glia" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v4_corpus_callosum_glia";
elif [ ${arg_tissue} = "pineal_gland" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v5_pineal_gland";
elif [ ${arg_tissue} = "peripheral_nerve" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v6_peripheral_nerve";
elif [ ${arg_tissue} = "spine" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v7_spine";
elif [ ${arg_tissue} = "retina" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v8_retina";
elif [ ${arg_tissue} = "eye" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v9_eye";
elif [ ${arg_tissue} = "artery_and_aorta" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v10_artery_aorta";
elif [ ${arg_tissue} = "vein" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v11_vein";
elif [ ${arg_tissue} = "lymphnode" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v12_lymphnode";
elif [ ${arg_tissue} = "peripheral_blood" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v13_peripheral_blood";
elif [ ${arg_tissue} = "spleen" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v14_spleen";
elif [ ${arg_tissue} = "thymus" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v15_thymus";
elif [ ${arg_tissue} = "bone_marrow" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v16_bone_marrow";
elif [ ${arg_tissue} = "adipose" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v17_adipose";
elif [ ${arg_tissue} = "bone" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v18_bone";
elif [ ${arg_tissue} = "skin" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v19_skin";
elif [ ${arg_tissue} = "uterus" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v20_uterus";
elif [ ${arg_tissue} = "placenta" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v21_placenta";
elif [ ${arg_tissue} = "prostate" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v22_prostate";
elif [ ${arg_tissue} = "ovary" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v23_ovary";
elif [ ${arg_tissue} = "testis" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v24_testis";
elif [ ${arg_tissue} = "heart" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v25_heart";
elif [ ${arg_tissue} = "muscle" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v26_muscle";
elif [ ${arg_tissue} = "esophagus" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v27_esophagus";
elif [ ${arg_tissue} = "stomach" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v28_stomach";
elif [ ${arg_tissue} = "intestine" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v29_intestine";
elif [ ${arg_tissue} = "colon" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v30_colon";
elif [ ${arg_tissue} = "liver_hepato" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v31_liver_hepato";
elif [ ${arg_tissue} = "lung" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v32_lung";
elif [ ${arg_tissue} = "bladder" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v33_bladder";
elif [ ${arg_tissue} = "kidney" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v34_kidney";
elif [ ${arg_tissue} = "pituitary" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v35_pituitary";
elif [ ${arg_tissue} = "thyroid_and_parathyroid" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v36_thyroid_parathyroid";
elif [ ${arg_tissue} = "adrenal_gland" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v37_adrenal_gland";
elif [ ${arg_tissue} = "pancreas" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v38_pancreas";
elif [ ${arg_tissue} = "breast" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v39_breast";
elif [ ${arg_tissue} = "salivary" ]; then
	echo "Refer to "${arg_tissue}" Expression Data";
	tissue_label="v40_salivary";
else
  echo "The "${arg_tissue}" is not allowed as the input. Please check the below help"
  usage
  echo "PROTECTiO.sh aborts..."
  exit 1;
fi

if [ ${arg_editor} = "ABE" ]; then
  echo "Sorry... The ${arg_editor} option has not yet been implemented. Please wait for a while."
  echo "PROTECTiO.sh aborts..."
  exit 1;
elif [ ${arg_editor} = "CBE" ] ]; then
  echo "Use "${arg_editor}" Prediction Model..."
else
  echo "The "${arg_editor}" is not allowed as the input. Please check the below help"
  usage
  echo "PROTECTiO.sh aborts..."
  exit 1;
fi

echo "Make output folder: "${arg_outpur_dir_name}
if [ ! -d ${arg_outpur_dir_name} ]; then
  mkdir ${arg_outpur_dir_name}
else
  echo "The output folder already existed!!! Choose a unique folder name."
  echo "PROTECTiO.sh aborts..."
  exit 1;
fi

echo "---------------------------------------------------------------------"
echo "|                  Download RefEx databases                         |"
echo "---------------------------------------------------------------------"
echo "Download RefEx database"
# Download RefEx database
mkdir ${arg_outpur_dir_name}/refex_db;
if [ ${arg_database} = "Human" ]; then
  # RefEx_sample_ann_genechip_human_GSE7307.tsv.zip
  wget -P ${arg_outpur_dir_name}/refex_db https://dx.doi.org/10.6084/m9.figshare.4028691;
  db_data="RefEx_sample_ann_genechip_human_GSE7307.tsv";
else
  echo "Unexpected Error."
  echo "Please contact the developers: kazukinakamae<at_makr>gmail.com"
  exit 1;
fi
echo "Uncompress "${db_data}".zip..."
unzip ${db_data}".zip";

echo "---------------------------------------------------------------------"
echo "|                  Retrieve Ensembl ID using Togo ID                 |"
echo "---------------------------------------------------------------------"

# @TODO：affy2ensg.pyを改変してコマンドライン引数を受け付けるようにする
python ./affy2ensg.py


echo "done."
echo "--------------------------------------------------------------"
echo "All process was successfully done!"
exit 0;