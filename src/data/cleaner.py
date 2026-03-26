import re
import pandas as pd
from pathlib import Path
from bson import ObjectId
from datetime import datetime, timezone


def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = re.sub(r'\[.*?\]', '', texto)       # quitar [chorus], [verse], etc.
    texto = re.sub(r'[^a-zA-Z\s]', '', texto)   # solo letras y espacios
    texto = texto.replace('\n', ' ')             # eliminar saltos de línea
    texto = re.sub(r'\s+', ' ', texto).strip()  # colapsar espacios dobles
    return texto


def limpiar_dataset_csv(df):
    """
    Limpia el dataset lyrics_dataset.csv y construye las columnas del esquema MongoDB.

    Columnas originales: Song, Song year, Artist, Genre, Lyrics, Track_id
    Columnas de salida  : _id, titulo, artista, genero, anio, letra,
                          idioma, fuente, url_fuente, fecha_recopilacion
    """

    cols_a_eliminar = ["Track_id"]
    df = df.drop(columns=[c for c in cols_a_eliminar if c in df.columns])


    resultado = pd.DataFrame()
    resultado["_id"]               = [str(ObjectId()) for _ in range(len(df))]
    resultado["Song"]            = df["Song"].str.strip()
    resultado["Artist"]           = df["Artist"].str.strip()
    resultado["Genre"]            = df["Genre"].str.strip()
    resultado["Song year"]              = pd.to_numeric(df["Song year"])
    resultado["Lyrics"]             = df["Lyrics"].apply(limpiar_texto)
    resultado["Language"]            = "en"
    resultado["Source"]            = "kaggle"
    resultado["Url"]        = "https://www.kaggle.com"
    resultado["collection_date"] = datetime.now(tz=timezone.utc).strftime("%d-%m-%Y")



    project_root = Path.cwd().parent
    output_path = project_root / "data" / "processed" / "lyrics_clean.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(output_path, index=False, encoding="utf-8")

    return resultado