"""
scraper_api.py
──────────────
Funciones de consulta a la API de Genius y scraping de letras.
No contiene lógica de limpieza (ver processing/lyrics_cleaner.py)
ni de persistencia (ver storage/mongo_storage.py).

CORRECCIÓN: el género ya no se extrae de los tags de Genius (poco fiables,
siempre devuelven "Pop"). Ahora se pasa explícitamente desde el CSV de artistas.
"""

import time
import requests
from bs4 import BeautifulSoup
import sys
import os

# 1. Obtenemos la ruta absoluta de la carpeta 'src'
ruta_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Agregamos 'src' al path si no está ya ahí
if ruta_src not in sys.path:
    sys.path.append(ruta_src)

# 3. Ahora el import funcionará sin importar desde dónde corras el código
from data.lyrics_cleaner import limpiar_letra

# ── Constantes ────────────────────────────────────────────────────────────────

GENIUS_API_BASE = "https://api.genius.com"
REQUEST_DELAY   = 1.0   # segundos de pausa entre peticiones (cortesía hacia Genius)


# ── Funciones de bajo nivel ───────────────────────────────────────────────────

def _get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def buscar_id_artista(nombre_artista: str, token: str) -> tuple[int | None, str | None]:
    """
    Busca el primer artista que coincida con `nombre_artista` en Genius.

    Retorna
    -------
    (artist_id, nombre_real) o (None, None) si no se encuentra.
    """
    headers = _get_headers(token)
    url = f"{GENIUS_API_BASE}/search?q={nombre_artista}"
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        for hit in res["response"]["hits"]:
            artist = hit["result"]["primary_artist"]
            return artist["id"], artist["name"]
    except Exception as e:
        print(f"[scraper] Error buscando artista '{nombre_artista}': {e}")
    return None, None


def _scrape_lyrics(url: str) -> str:
    """Descarga y extrae la letra cruda desde la página de Genius."""
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.text, "html.parser")

    containers = soup.select('div[class^="Lyrics__Container"]')
    if containers:
        return "\n".join(c.get_text(separator="\n") for c in containers)

    # Fallback para páginas en formato antiguo
    legacy = soup.find("div", class_="lyrics")
    return legacy.get_text() if legacy else ""


def _extraer_detalle_cancion(
    song_item: dict,
    nombre_real: str,
    genero: str,           # ← recibido desde el CSV, no de Genius
    token: str,
) -> dict | None:
    """
    Dado un ítem de la lista de canciones, consulta el detalle y hace el scraping.
    Retorna un dict con la información de la canción o None si hay error.
    """
    headers = _get_headers(token)
    titulo  = song_item["title"]

    try:
        res_detail = requests.get(
            f"{GENIUS_API_BASE}/songs/{song_item['id']}",
            headers=headers,
            timeout=10
        ).json()
        s = res_detail["response"]["song"]

        # Año de lanzamiento
        release = s.get("release_date") or ""
        anio    = release.split("-")[0] if release else "N/A"

        # Letra limpia
        letra_raw    = _scrape_lyrics(s["url"])
        letra_limpia = limpiar_letra(letra_raw)

        return {
            "Song":      titulo,
            "Artist":    nombre_real,
            "Genre":     genero,           # ← género del CSV, no de Genius tags
            "Song year": anio,
            "Language":  s.get("language", "n/a"),
            "Url":       s.get("url"),
            "Lyrics":    letra_limpia,
        }

    except Exception as e:
        print(f"  [scraper] Error procesando '{titulo}': {e}")
        return None


# ── Función principal ─────────────────────────────────────────────────────────

def extraer_canciones_artista(
    nombre: str,
    genero: str,
    token: str,
    cantidad: int = 2,
) -> list[dict]:
    """
    Extrae las `cantidad` canciones más populares de un artista en Genius.

    Parámetros
    ----------
    nombre   : str  – Nombre del artista a buscar.
    genero   : str  – Género del artista (viene del CSV, no de Genius).
    token    : str  – Token de acceso a la API de Genius.
    cantidad : int  – Número de canciones a extraer (default 2).

    Retorna
    -------
    list[dict] – Lista de diccionarios con la información de cada canción.
    """
    artist_id, nombre_real = buscar_id_artista(nombre, token)

    if not artist_id:
        print(f"[scraper] No se encontró al artista: {nombre}")
        return []

    print(f"\n{'─'*50}")
    print(f" Extrayendo {cantidad} canciones de: {nombre_real} [{genero}]")
    print(f"{'─'*50}")

    api_url = (
        f"{GENIUS_API_BASE}/artists/{artist_id}/songs"
        f"?per_page={cantidad}&sort=popularity"
    )
    headers = _get_headers(token)

    try:
        res = requests.get(api_url, headers=headers, timeout=10).json()
    except Exception as e:
        print(f"[scraper] Error obteniendo canciones de {nombre_real}: {e}")
        return []

    canciones = []
    for song_item in res["response"]["songs"]:
        print(f"  → {song_item['title']}")
        datos = _extraer_detalle_cancion(song_item, nombre_real, genero, token)
        if datos:
            canciones.append(datos)
        time.sleep(REQUEST_DELAY)

    print(f"  ✓ {len(canciones)} canciones obtenidas de {nombre_real}\n")
    return canciones


def extraer_multiples_artistas(
    lista_artistas: list[dict],
    token: str,
    cantidad: int = 10,
) -> list[dict]:
    """
    Itera sobre una lista de artistas y extrae sus canciones.

    Parámetros
    ----------
    lista_artistas : list[dict]  – Cada elemento debe tener 'artist' y 'genre'.
                                   Ejemplo: [{"artist": "Taylor Swift", "genre": "Pop"}, ...]
    token          : str         – Token de acceso a la API de Genius.
    cantidad       : int         – Canciones por artista (default 10).

    Retorna
    -------
    list[dict] – Lista unificada con las canciones de todos los artistas.
    """
    todas = []
    for item in lista_artistas:
        nombre = item["artist"]
        genero = item["genre"]
        canciones = extraer_canciones_artista(nombre, genero, token, cantidad)
        todas.extend(canciones)
    return todas