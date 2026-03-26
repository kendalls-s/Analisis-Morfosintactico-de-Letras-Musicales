# src/__init__.py
# Exporta todo lo necesario del scraper para que el import funcione
# sin importar desde qué carpeta se ejecute el notebook.

from src.scraper import (
    scrape_azlyrics,
    get_artist_songs,
    get_lyrics,
    GENRE_ARTISTS,
    BASE_URL,
    HEADERS,
)

__all__ = [
    "scrape_azlyrics",
    "get_artist_songs",
    "get_lyrics",
    "GENRE_ARTISTS",
    "BASE_URL",
    "HEADERS",
]
