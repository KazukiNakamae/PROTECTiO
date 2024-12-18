import sys
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

__authors__ = ["Kazuki Nakamae"]
__version__ = "1.0.0"

def pred_rna_offtarget(dna, model_dir):
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # モデル仕様に利用するデバイスの設定：CUDAが使えなければCPUを使うように設定
        tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True) # 訓練済みモデルが理解できるフォーマットを指定
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, trust_remote_code=True).to(device) # 分類処理用に訓練済みモデルを読み込み
    except Exception as e:
        print(f"Error loading model from {model_dir}: {e}")
        sys.exit(1)

    inputs = tokenizer(dna, return_tensors='pt') # 入力テキストを訓練済みモデルが理解できるフォーマット（トークン）に分割し、各トークンを「トークンID」に変換
    model.eval() # モデルの状態を推論モード（訓練モードでない）に指定
    with torch.no_grad():# テンソルの勾配計算OFF：省メモリ化
      # モデルのインプットとして渡して評価
      outputs = model(
          inputs["input_ids"].to(device), 
          inputs["attention_mask"].to(device),
        )
    # print(outputs.logits)
    # 例：tensor([[-1.6488,  1.4636]])という形で出力
    # [Negativeの評価値, Positiveの評価値]というような形式となっている。
    y_preds = np.argmax(outputs.logits.to('cpu').detach().numpy().copy(), axis=1) # 評価値が高い方のインデックス取り出し+numpy化
    
    # モデルからラベル判定を読み出す
    def id2label(x):
        return model.config.id2label[x]
    y_dash = [id2label(x) for x in y_preds] # 評価値が高い方のラベル判定を取り出す
    print(y_dash)
    # 例：['LABEL_1']という形で出力
    # LABEL_0: Negative / LABEL_1: Positive という意味
    return (dna, y_dash)

def print_usage():
    print(f"Usage: {sys.argv[0]} <input DNA sequence> <DNABERT-2 model directory>")
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
    
    dna = sys.argv[1]
    model_dir = sys.argv[2]

    pred_rna_offtarget(dna, model_dir)
