import pandas as pd
import requests
import json
import time

# read a tsv file and make a dataframe
df = pd.read_csv('RefEx_tissue_specific_genechip_human_GSE7307.tsv', sep='\t')
# get the first column
id_list = df.iloc[:, 0]
# get the first column as a list
id_list = df.iloc[:, 0].tolist()

id_split = [id_list[i : i + 500] for i in range(0, len(id_list), 500)]
print(len(id_split))

affyprobe_enst_list = []
for i in id_split:
    input = ','.join(i)
    url = f'https://api.togoid.dbcls.jp/convert?ids={input}&route=affy_probeset,ensembl_transcript&report=all&format=json'
    r = requests.get(url)
    print(r.json())
    affyprobe_enst_list.append(r.json())
    time.sleep(0.5)

# write out a json file
with open('affyprobe_enst.json', 'w') as f:
    json.dump(affyprobe_enst_list, f, indent=4)