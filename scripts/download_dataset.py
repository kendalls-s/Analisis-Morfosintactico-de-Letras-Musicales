import os
import subprocess
import sys
import zipfile

RAW_DIR = "data/raw"
DATASET = "mateibejan/multilingual-lyrics-for-genre-classification"
ZIP_NAME = "multilingual-lyrics-for-genre-classification.zip"

def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    print("Descargando dataset desde Kaggle...")

    subprocess.run([
        sys.executable, "-m", "kaggle",
        "datasets", "download",
        "-d", DATASET,
        "-p", RAW_DIR
    ], check=True)

    # Descomprimir
    zip_path = os.path.join(RAW_DIR, ZIP_NAME)

    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DIR)
        os.remove(zip_path)

    print("Dataset descargado y listo en data/raw/")

if __name__ == "__main__":
    main()
