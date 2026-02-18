import re
from pathlib import Path
def limpiar_dataset(df):
    """
    Limpia el dataset de letras:
    - Elimina columna Track_id si existe
    - Limpia el texto de la columna Lyrics
    - Crea columna Clean_Lyrics
    """

    # Eliminar columna innecesaria
    if "Track_id" in df.columns:
        df = df.drop("Track_id", axis=1)

    # Función interna para limpiar texto
    def limpiar_texto(texto):
        texto = re.sub(r'\[.*?\]', '', texto)      # eliminar [chorus], etc.
        texto = re.sub(r'[^a-zA-Z\s]', '', texto)  # eliminar caracteres especiales
        texto = re.sub(r'\s+', ' ', texto).strip() # eliminar espacios dobles
        texto = texto.replace('\n', ' ') #eliminar saltos de renglon

        return texto

    # Aplicar limpieza
    df["Lyrics"] = df["Lyrics"].apply(limpiar_texto)

    # Construir ruta destino
    project_root = Path.cwd().parent
    output_path = project_root / "data" / "processed" / "lyrics_clean.csv"

    # Guardar archivo
    df.to_csv(output_path, index=False, encoding="utf-8")

    return df
