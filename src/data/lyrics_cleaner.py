"""
lyrics_cleaner.py
─────────────────
Funciones de limpieza de letras crudas obtenidas de Genius.
Separado del scraper para poder importarse de forma independiente.
"""

import re


def limpiar_letra(letra_raw: str) -> str:
    """
    Limpia una letra cruda extraída de Genius en dos fases:
      A) Limpieza estructural – conserva estrofas, elimina metadatos.
      B) Limpieza para NLP – colapsa en una línea, elimina puntuación y números.

    Parámetros
    ----------
    letra_raw : str
        Texto crudo devuelto por BeautifulSoup.

    Retorna
    -------
    str
        Letra limpia lista para procesamiento, o "N/A" si la entrada es vacía.
    """
    if not letra_raw:
        return "N/A"

    # ── FASE A: LIMPIEZA ESTRUCTURAL ──────────────────────────────────────────

    # 1. Recortar todo lo anterior a la palabra "Lyrics" (menús, traducciones…)
    if "Lyrics" in letra_raw:
        letra = letra_raw.split("Lyrics", 1)[-1]
    else:
        letra = letra_raw

    # 2. Eliminar metadatos de Contributors
    letra = re.sub(
        r'^\d+\s*Contributors.*?\n', '',
        letra,
        flags=re.IGNORECASE | re.MULTILINE
    )

    # 3. Eliminar bloque "Read More"
    letra = re.sub(
        r'^.*?\n.*?Read More', '',
        letra,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 4. Eliminar etiquetas de sección: [Verse 1], [Chorus], [Bridge], etc.
    letra = re.sub(r'\[.*?\]', '', letra)

    # 5. Eliminar "Embed" y numerales basura al final
    letra = re.sub(r'\d*Embed$', '', letra).strip()

    # ── FASE B: LIMPIEZA PARA NLP ─────────────────────────────────────────────

    # 6. Saltos de línea → espacio (una sola línea de datos)
    letra = letra.replace('\n', ' ')

    # 7. Conservar sólo letras latinas (incl. tildes y ñ) y espacios
    letra = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]', '', letra)

    # 8. Colapsar espacios múltiples
    letra = re.sub(r'\s+', ' ', letra).strip()

    return letra if letra else "N/A"
