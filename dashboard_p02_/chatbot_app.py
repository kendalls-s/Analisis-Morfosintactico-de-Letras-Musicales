"""
chatbot_app.py
──────────────
MúsicBot — Chatbot Musical Inteligente con RAG + Fine-Tuning
Línea A: Clasificador de Géneros (Rock, Hip-Hop, Metal)

Ubicación esperada:  dashboard_p02_/pages/chatbot_app.py
"""

import os
import sys
import json
import threading
import numpy as np
from datetime import datetime
from functools import lru_cache

# ── Resolver raíz del proyecto (dashboard_p02_/) ──────────────────────────────
THIS_FILE    = os.path.abspath(__file__)
PAGES_DIR    = os.path.dirname(THIS_FILE)
PROJECT_ROOT = os.path.dirname(PAGES_DIR)

# Agregar src/Proyecto_3 al path para importar rag_utils / finetuning_utils
SRC_P3 = os.path.join(PROJECT_ROOT, "src", "Proyecto_3")
if SRC_P3 not in sys.path:
    sys.path.insert(0, SRC_P3)

# Rutas absolutas de datos y modelos
DATA_DIR        = os.path.join(PROJECT_ROOT, "data")
EMBED_CACHE_DIR = os.path.join(DATA_DIR, "embeddings_cache")
EMBED_CACHE     = os.path.join(EMBED_CACHE_DIR, "embeddings.npy")
CHUNKS_CACHE    = os.path.join(EMBED_CACHE_DIR, "chunks.pkl")
MODEL_DIR       = os.path.join(PROJECT_ROOT, "models", "clasificador_genero")
LABEL_FILE      = os.path.join(MODEL_DIR, "label_encoder.json")

# ── Dash ───────────────────────────────────────────────────────────────────────
import dash
from dash import dcc, html, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc

# ── Constantes ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAEwaM4J3Y72jACC5RJh72onIblaXaVS2E")
GENEROS = ["Rock", "Hip-Hop", "Metal"]

# ── Prompt de sistema — INMUTABLE ──────────────────────────────────────────────
_SYSTEM_PROMPT = """Eres MúsicBot, un experto apasionado en géneros musicales.
Tu dominio es EXCLUSIVAMENTE música: géneros musicales (Rock, Hip-Hop, Metal y sus subgéneros),
letras de canciones, artistas, historia de la música y análisis lírico.

REGLAS DE CONTENIDO (inamovibles):
1. Solo respondes sobre música, géneros musicales, artistas o letras de canciones.
2. SIEMPRE que el CONTEXTO RAG contenga canciones, ÚSALAS. Menciona título y artista.
   NUNCA digas que no tienes canciones si las hay en el contexto.
3. Las letras del corpus están en INGLÉS, pero tú DEBES responder y explicar en ESPAÑOL.
   Si el usuario busca un concepto (ej. "guerra"), explica cómo la letra en inglés se relaciona con eso.
4. Si el usuario pide VARIOS géneros, recomienda canciones de CADA género solicitado
   en secciones separadas, no mezcles ni ignores ninguno.
5. Si la pregunta no es sobre música, responde educadamente que solo puedes hablar de música.
6. Mantén siempre un tono amable, entusiasta y educado.

REGLAS DE FORMATO (obligatorias en cada respuesta):
- Usa una intro corta de 1-2 líneas, sin párrafos largos iniciales.
- Para recomendaciones: presenta cada canción en un bloque visual claro:
    🎵 **"Título"** — Artista (Año)
    ➤ Por qué encaja: [1-2 oraciones concretas en ESPAÑOL basadas en la letra en INGLÉS]
- Si hay varios géneros, agrúpalos con un encabezado:
    ### 🤘 Metal  /  ### 🎤 Hip-Hop  /  ### 🎸 Rock
- Termina con una línea de cierre corta y animada.
- NUNCA escribas bloques de texto denso de más de 3 líneas seguidas."""

_FUERA_DE_DOMINIO = (
    "¡Hola! Soy MúsicBot y me especializo exclusivamente en música, géneros musicales y "
    "letras de canciones. No puedo ayudarte con ese tema, pero si tienes preguntas sobre "
    "Rock, Hip-Hop, Metal, artistas o cualquier curiosidad musical, ¡con gusto te ayudo! 🎵"
)

_MUSIC_KW = {
    "canción","cancion","música","musica","artista","banda","grupo","género","genero",
    "rock","hip-hop","hiphop","hip","hop","metal","rap","letra","estrofa","coro","álbum","album",
    "disco","lyric","song","music","artist","genre","beat","ritmo","melodía","melodia",
    "riff","vocal","guitarra","batería","bateria","bajo","sintetizador","recomienda",
    "recomendar","busca","buscar","cuéntame","cuentame","explica","explícame","explicame",
    "diferencia","comparar","compara","pop","jazz","reggae","reggaeton","blues","punk",
    "indie","heavy","clásico","clasico","underground","mainstream","spotify","concierto",
    "festival","tour","discografía","discografia","subgénero","subgenero","sonido",
    "influencia","influencias","cantar","compositor","compositora","producción","produccion",
    "lirica","lírica","verso","versos","flow","rima","rimas","sample","sampling",
    "calle","barrio","trap","freestyle","boom","bap","gangsta","west","east","coast",
}

# ── Estado global lazy-loaded ──────────────────────────────────────────────────
_embed_model   = None
_faiss_index   = None
_chunks        = None
_clf_model     = None
_clf_tokenizer = None
_clf_labels    = None
_flan_pipeline = None
_model_lock    = threading.Lock()


# ══════════════════════════════════════════════════════════════════════════════
#  RAG helpers
# ══════════════════════════════════════════════════════════════════════════════

def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        with _model_lock:
            if _embed_model is None:
                from sentence_transformers import SentenceTransformer
                print("[MúsicBot] Cargando modelo de embeddings...")
                _embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
                print("[MúsicBot] ✓ Modelo de embeddings listo")
    return _embed_model

def _load_rag_index():
    global _faiss_index, _chunks
    import faiss, pickle

    if not os.path.exists(EMBED_CACHE) or not os.path.exists(CHUNKS_CACHE):
        print(f"[MúsicBot] ⚠ Caché RAG no encontrada en {EMBED_CACHE_DIR}")
        return False

    print("[MúsicBot] Cargando índice FAISS desde caché...")
    embeddings = np.load(EMBED_CACHE)
    with open(CHUNKS_CACHE, "rb") as f:
        _chunks = pickle.load(f)

    faiss.normalize_L2(embeddings)
    _faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
    _faiss_index.add(embeddings)
    print(f"[MúsicBot] ✓ Índice listo — {_faiss_index.ntotal} vectores")
    return True

@lru_cache(maxsize=256)
def _encode_query(query: str) -> np.ndarray:
    model = _get_embed_model()
    import faiss
    q_emb = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q_emb)
    return q_emb

def _search_rag(query: str, top_k: int = 5, genre_filter: str = None) -> list:
    global _faiss_index, _chunks
    if _faiss_index is None or _chunks is None:
        if not _load_rag_index():
            return []
    import faiss

    q_emb = _encode_query(query)
    search_k = min(top_k * 20 if genre_filter else top_k * 4, len(_chunks))
    scores, indices = _faiss_index.search(q_emb, search_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        chunk = _chunks[idx]
        if genre_filter:
            chunk_genre = chunk.get("genre", "").strip().lower()
            target      = genre_filter.strip().lower()
            if chunk_genre.replace("-", "").replace(" ", "") != target.replace("-", "").replace(" ", ""):
                continue
        results.append({**chunk, "score": float(score)})
        if len(results) >= top_k:
            break
    return results


# ══════════════════════════════════════════════════════════════════════════════
#  Clasificador fine-tuneado
# ══════════════════════════════════════════════════════════════════════════════

def _load_classifier() -> bool:
    global _clf_model, _clf_tokenizer, _clf_labels
    if _clf_model is not None:
        return True
    if not os.path.exists(MODEL_DIR) or not os.path.exists(LABEL_FILE):
        return False
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        _clf_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        _clf_model     = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        _clf_model.eval()
        with open(LABEL_FILE) as f:
            _clf_labels = json.load(f)["classes"]
        return True
    except Exception as e:
        print(f"[MúsicBot] ⚠ No se pudo cargar el clasificador: {e}")
        return False

def _classify_genre(text: str):
    if not _load_classifier():
        return None
    import torch
    # Sincronizado con finetuning_utils.py: max_length=256
    enc = _clf_tokenizer(
        text[:512], return_tensors="pt", truncation=True, padding=True, max_length=256
    )
    with torch.no_grad():
        logits = _clf_model(**enc).logits
    return _clf_labels[logits.argmax(-1).item()]


# ══════════════════════════════════════════════════════════════════════════════
#  Detección Inteligente
# ══════════════════════════════════════════════════════════════════════════════

def _is_music_related(text: str) -> bool:
    text_lower = text.lower()
    tokens = set(text_lower.replace("-", " ").split())

    # 1. Chequeo por palabras clave musicales explícitas
    if bool(tokens & _MUSIC_KW):
        return True

    # 2. Chequeo por intención de búsqueda semántica
    busquedas_semanticas = [
        "algo que", "que diga", "que hable", "que trate",
        "frase", "como:", "sobre", "letras de", "relacionado con"
    ]
    if any(frase in text_lower for frase in busquedas_semanticas):
        return True

    return False

def _detect_genres_in_query(text: str) -> list:
    tl = text.lower().replace("-", " ")
    tokens = set(tl.split())
    found = []
    if any(w in tl for w in ["hip hop", "hiphop", "rappero", "rapero"]) or \
       any(w in tokens for w in ["rap", "trap", "freestyle", "flow", "rima", "beat", "hip", "hop"]):
        found.append("Hip-Hop")
    if any(w in tokens for w in ["metal", "heavy", "thrash"]) or "death metal" in tl:
        found.append("Metal")
    if any(w in tokens for w in ["rock", "punk", "grunge"]):
        found.append("Rock")
    return found


# ══════════════════════════════════════════════════════════════════════════════
#  Construcción de prompt
# ══════════════════════════════════════════════════════════════════════════════

def _build_context_block(chunks: list, genres: list = None) -> str:
    if not chunks:
        return ""
    by_genre = {}
    for c in chunks[:8]:
        g = c.get("genre", "?")
        by_genre.setdefault(g, []).append(c)

    parts = []
    for g, cs in by_genre.items():
        parts.append(f"--- Género: {g} ---")
        for c in cs:
            parts.append(
                f"  Título  : {c.get('song', '?')}\n"
                f"  Artista : {c.get('artist', '?')}\n"
                f"  Año     : {c.get('year', '?')}\n"
                f"  Relevancia: {int(c.get('score', 0) * 100)}%\n"
                f"  Letra   : \"{c.get('texto', '')[:250]}...\""
            )
    return "\n\n".join(parts)

def _build_full_prompt(user_msg: str, history: list, context_block: str, genres: list = None) -> str:
    hist_lines = []
    for m in history[-6:]:
        role = "Usuario" if m["role"] == "user" else "MúsicBot"
        hist_lines.append(f"{role}: {m['content']}")
    hist_str = "\n".join(hist_lines)

    genre_instruction = ""
    if genres and len(genres) > 1:
        genre_instruction = (
            f"\nIMPORTANTE: El usuario pidió VARIOS géneros: {', '.join(genres)}. "
            f"DEBES recomendar canciones de CADA uno en secciones separadas."
        )
    elif genres:
        genre_instruction = f"\nGénero solicitado/detectado: {genres[0]}. Privilegia este género si es posible."

    if context_block:
        rag_section = (
            f"\n\n=== CANCIONES DEL CORPUS (úsalas todas) ==={genre_instruction}\n"
            f"{context_block}\n"
            f"=== FIN CORPUS ==="
        )
    else:
        # Prompt restrictivo para cuando el RAG está apagado
        rag_section = (
            f"\n\n(Sin canciones en el corpus.{genre_instruction} "
            f"Habla teóricamente del género y sus características, pero TIENES ESTRICTAMENTE PROHIBIDO "
            f"recomendar canciones específicas o inventar títulos. Si el usuario te pide una canción o letra, "
            f"indica claramente que sin el contexto RAG activado no puedes buscar en tu base de datos.)"
        )

    return (
        f"{_SYSTEM_PROMPT}"
        f"{rag_section}\n\n"
        f"HISTORIAL:\n{hist_str}\n\n"
        f"Usuario: {user_msg}\n"
        f"MúsicBot:"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  Generadores LLM
# ══════════════════════════════════════════════════════════════════════════════

_gemini_model  = None
_gemini_apikey = None

def _gen_gemini(prompt: str, api_key: str) -> str:
    global _gemini_model, _gemini_apikey
    import google.generativeai as genai
    if _gemini_model is None or api_key != _gemini_apikey:
        genai.configure(api_key=api_key)
        _gemini_model  = genai.GenerativeModel("gemini-2.5-flash")
        _gemini_apikey = api_key
    resp = _gemini_model.generate_content(prompt)
    return resp.text.strip()

def _gen_flan(prompt: str) -> str:
    global _flan_pipeline
    if _flan_pipeline is None:
        from transformers import pipeline
        try:
            _flan_pipeline = pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=300)
        except Exception:
            _flan_pipeline = pipeline("text-generation", model="google/flan-t5-base", max_new_tokens=300)
    result = _flan_pipeline(prompt[-1800:], max_new_tokens=300)
    out = result[0]
    return (out.get("generated_text") or out.get("summary_text") or "").strip()


# ══════════════════════════════════════════════════════════════════════════════
#  Pipeline principal
# ══════════════════════════════════════════════════════════════════════════════

def chatbot_respond(user_msg: str, history: list, model_choice: str, api_key: str, use_rag: bool = True):

    if not _is_music_related(user_msg):
        return _FUERA_DE_DOMINIO, []

    genres = _detect_genres_in_query(user_msg)
    if not genres:
        single = _classify_genre(user_msg)
        genres = [single] if single else []

    all_chunks = []

    if use_rag:
        if genres:
            per_genre = max(3, 6 // len(genres))
            seen_ids  = set()
            for g in genres:
                g_chunks = _search_rag(user_msg, top_k=per_genre, genre_filter=g)
                for c in g_chunks:
                    uid = (c.get('song',''), c.get('artist',''))
                    if uid not in seen_ids:
                        seen_ids.add(uid)
                        all_chunks.append(c)

        if not all_chunks:
            all_chunks = _search_rag(user_msg, top_k=5)
    else:
        print("[MúsicBot] Generando respuesta SIN contexto RAG para comparativa.")

    context_block = _build_context_block(all_chunks, genres) if use_rag else ""
    full_prompt   = _build_full_prompt(user_msg, history, context_block, genres)

    try:
        if model_choice == "gemini" and api_key and api_key.strip():
            answer = _gen_gemini(full_prompt, api_key.strip())
        else:
            answer = _gen_flan(full_prompt)
    except Exception as e:
        answer = f"⚠️ Error al generar la respuesta: {e}"

    return answer, all_chunks


# ══════════════════════════════════════════════════════════════════════════════
#  Design tokens y UI
# ══════════════════════════════════════════════════════════════════════════════

C = {
    "bg":      "#08080e", "surface":  "#0f0f18", "surface2": "#171722",
    "border":  "#252535", "accent":   "#c8f564", "accent2":  "#8aaa40",
    "violet":  "#7c3aed", "orange":   "#f97316", "text":     "#e8e8f0",
    "muted":   "#5a5a70", "rock":     "#ef4444", "hiphop":   "#f59e0b",
    "metal":   "#8b5cf6",
}

CSS = f"""
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ height: 100%; overflow: hidden; }}
body {{
  font-family: 'DM Sans', sans-serif; background: {C['bg']}; color: {C['text']}; height: 100vh;
}}
#shell {{ display:flex; height:100vh; overflow:hidden; }}

#sidebar {{
  width: 272px; min-width: 272px; background: {C['surface']}; border-right: 1px solid {C['border']};
  display: flex; flex-direction: column; overflow: hidden;
}}
#sb-head {{ padding: 26px 22px 18px; border-bottom: 1px solid {C['border']}; flex-shrink: 0; }}
.logo {{ font-family:'Syne',sans-serif; font-weight:800; font-size:21px; color:{C['accent']}; letter-spacing:-0.5px; }}
.logo-tagline {{ font-size:10px; color:{C['muted']}; letter-spacing:2.5px; text-transform:uppercase; margin-top:3px; }}
#sb-body {{ padding: 18px 14px; flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:18px; }}
.sb-label {{ font-size:9px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:{C['muted']}; margin-bottom:7px; }}
.Select-control {{ background:{C['surface2']} !important; border:1px solid {C['border']} !important; border-radius:9px !important; color:{C['text']} !important; font-family:'DM Sans',sans-serif !important; min-height:40px !important; }}
.Select-menu-outer {{ background:{C['surface2']} !important; border:1px solid {C['border']} !important; border-radius:9px !important; }}
.Select-option {{ background:{C['surface2']} !important; color:{C['text']} !important; }}
.Select-option:hover,.Select-option.is-focused {{ background:{C['border']} !important; }}
.Select-value-label {{ color:{C['text']} !important; }}
.Select-arrow {{ border-top-color:{C['muted']} !important; }}
.api-inp {{ width:100%; background:{C['surface2']}; border:1px solid {C['border']}; border-radius:9px; color:{C['text']}; font-family:'DM Sans',sans-serif; font-size:13px; padding:10px 12px; outline:none; }}
.api-inp:focus {{ border-color:{C['accent']}88; box-shadow:0 0 0 3px {C['accent']}18; }}
.g-wrap {{ display:flex; flex-direction:column; gap:6px; }}
.gbadge {{ display:inline-flex; align-items:center; gap:6px; padding:5px 11px; border-radius:20px; font-size:11px; font-weight:600; width:fit-content; }}
.g-rock  {{ background:{C['rock']}1a;   color:{C['rock']};   border:1px solid {C['rock']}44;   }}
.g-hip   {{ background:{C['hiphop']}1a; color:{C['hiphop']}; border:1px solid {C['hiphop']}44; }}
.g-metal {{ background:{C['metal']}1a;  color:{C['metal']};  border:1px solid {C['metal']}44;  }}
.clear-btn {{ background:transparent; border:1px solid {C['border']}; border-radius:8px; color:{C['muted']}; font-size:11px; padding:7px 11px; cursor:pointer; font-family:'DM Sans',sans-serif; text-align:left; width:100%; }}
.clear-btn:hover {{ border-color:{C['orange']}66; color:{C['orange']}; }}
#chunks-wrap {{ flex:1; overflow:hidden; display:flex; flex-direction:column; min-height:0; }}
#chunks-inner {{ flex:1; overflow-y:auto; }}
#chunks-inner::-webkit-scrollbar {{ width:3px; }}
#chunks-inner::-webkit-scrollbar-thumb {{ background:{C['border']}; border-radius:2px; }}
.chunk-card {{ background:{C['surface2']}; border:1px solid {C['border']}; border-radius:9px; padding:11px; margin-bottom:7px; }}
.chunk-top {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:5px; }}
.chunk-score {{ font-family:'Syne',sans-serif; font-weight:700; font-size:10px; color:{C['accent']}; }}
.chunk-meta {{ font-size:11px; color:{C['muted']}; line-height:1.5; margin-bottom:5px; }}
.chunk-lyric {{ font-size:11px; color:{C['text']}99; border-left:2px solid {C['border']}; padding-left:7px; font-style:italic; line-height:1.55; }}

#main {{ flex:1; display:flex; flex-direction:column; overflow:hidden; position:relative; background:{C['bg']}; }}
#chat-hdr {{ position:relative; z-index:1; padding:16px 26px; border-bottom:1px solid {C['border']}; display:flex; align-items:center; gap:10px; background:{C['surface']}cc; flex-shrink:0; }}
.dot-live {{ width:8px; height:8px; border-radius:50%; background:{C['accent']}; animation:blink 2s infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}
#hdr-title {{ font-family:'Syne',sans-serif; font-weight:700; font-size:15px; }}
#hdr-sub {{ font-size:11px; color:{C['muted']}; }}
#model-badge {{ margin-left:auto; background:{C['accent']}18; border:1px solid {C['accent']}44; color:{C['accent']}; font-size:10px; font-weight:700; padding:4px 9px; border-radius:20px; }}

#msgs {{ position:relative; z-index:1; flex:1; overflow-y:auto; padding:22px 26px; display:flex; flex-direction:column; gap:14px; scroll-behavior:smooth; }}
#msgs::-webkit-scrollbar {{ width:4px; }}
#msgs::-webkit-scrollbar-thumb {{ background:{C['border']}; border-radius:2px; }}
.row {{ display:flex; gap:10px; max-width:82%; }}
.row.u {{ margin-left:auto; flex-direction:row-reverse; }}
.av {{ width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; align-self:flex-start; margin-top:2px; }}
.av-bot  {{ background:{C['accent']}1a; border:1px solid {C['accent']}44; }}
.av-user {{ background:{C['violet']}2a; border:1px solid {C['violet']}55; }}
.bbl {{ padding:12px 15px; border-radius:13px; font-size:13.5px; line-height:1.68; word-break:break-word; max-width:100%; }}
.bbl-bot {{ background:{C['surface2']}; border:1px solid {C['border']}; border-radius:3px 13px 13px 13px; color:{C['text']}; }}
.bbl-u   {{ background:{C['violet']}2a; border:1px solid {C['violet']}44; border-radius:13px 3px 13px 13px; color:{C['text']}; }}

#inp-area {{ position:relative; z-index:1; padding:16px 26px; border-top:1px solid {C['border']}; background:{C['surface']}cc; flex-shrink:0; }}
#inp-row {{ display:flex; gap:9px; align-items:flex-end; }}
#chat-inp {{ flex:1; background:{C['surface2']}; border:1px solid {C['border']}; border-radius:12px; color:{C['text']}; font-family:'DM Sans',sans-serif; font-size:13.5px; padding:13px 15px; outline:none; resize:none; min-height:48px; max-height:110px; line-height:1.55; overflow-y:auto; }}
#chat-inp:focus {{ border-color:{C['accent']}77; }}
#send-btn {{ width:48px; height:48px; flex-shrink:0; background:{C['accent']}; border:none; border-radius:12px; cursor:pointer; font-size:18px; color:{C['bg']}; display:flex; align-items:center; justify-content:center; transition:transform .15s, background .15s; }}
#send-btn:hover  {{ transform:scale(1.06); background:#d4fb70; }}
.hint {{ font-size:11px; color:{C['muted']}; text-align:center; margin-top:7px; }}
#welcome {{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; padding:32px 20px; text-align:center; }}
.w-icon {{ font-size:46px; margin-bottom:6px; }}
.w-title {{ font-family:'Syne',sans-serif; font-weight:800; font-size:22px; color:{C['accent']}; }}
.w-desc {{ font-size:13px; color:{C['muted']}; max-width:340px; line-height:1.65; }}
.chips {{ display:flex; flex-wrap:wrap; gap:7px; justify-content:center; margin-top:14px; }}
.chip {{ background:{C['surface2']}; border:1px solid {C['border']}; border-radius:20px; padding:7px 13px; font-size:12px; color:{C['text']}bb; cursor:pointer; }}
.chip:hover {{ border-color:{C['accent']}66; color:{C['accent']}; }}
.md-h2 {{ font-family:'Syne',sans-serif; font-weight:700; font-size:14px; color:{C['accent']}; margin:10px 0 4px; }}
.md-h3 {{ font-family:'Syne',sans-serif; font-weight:600; font-size:13px; color:{C['accent']}cc; margin:8px 0 3px; border-bottom:1px solid {C['border']}; padding-bottom:3px; }}
.md-song-line {{ background:{C['surface']}; border-left:3px solid {C['accent']}77; border-radius:0 7px 7px 0; padding:6px 10px; margin:5px 0; font-size:13px; }}
.md-p {{ font-size:13.5px; line-height:1.7; margin:2px 0; }}
"""

def _welcome_screen():
    return html.Div(id="welcome", children=[
        html.Div("🎸", className="w-icon"),
        html.Div("¡Hola, soy MúsicBot!", className="w-title"),
        html.Div(
            "Tu experto en géneros musicales. Pregúntame sobre Rock, Hip-Hop y Metal: "
            "letras, artistas, diferencias de estilo y más.",
            className="w-desc"
        ),
        html.Div(className="chips", children=[
            html.Div("¿Qué diferencia al Rock del Metal?",       className="chip", id="chip-1"),
            html.Div("Recomiéndame una canción de Hip-Hop",       className="chip", id="chip-2"),
            html.Div("¿Qué caracteriza el rap lírico?",           className="chip", id="chip-3"),
            html.Div("Canciones de Metal que hablen de libertad", className="chip", id="chip-4"),
        ]),
    ])

def _parse_markdown_to_dash(text: str) -> list:
    children = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            children.append(html.Br())
            continue
        if stripped.startswith("### "):
            children.append(html.Div(stripped[4:], className="md-h3"))
        elif stripped.startswith("## "):
            children.append(html.Div(stripped[3:], className="md-h2"))
        elif stripped.startswith("🎵") or stripped.startswith("➤"):
            children.append(html.Div(_inline_bold(stripped), className="md-song-line"))
        else:
            children.append(html.Div(_inline_bold(stripped), className="md-p"))
    return children

def _inline_bold(text: str) -> list:
    import re
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    result = []
    for p in parts:
        if p.startswith("**") and p.endswith("**"):
            result.append(html.Strong(p[2:-2]))
        else:
            result.append(p)
    return result

def _render_messages(history: list):
    if not history:
        return [_welcome_screen()]
    items = []
    for msg in history:
        is_u = msg["role"] == "user"
        content_children = (
            [msg["content"]] if is_u else _parse_markdown_to_dash(msg["content"])
        )
        items.append(html.Div(
            className=f"row {'u' if is_u else ''}",
            children=[
                html.Div("👤" if is_u else "🎵",
                         className=f"av {'av-user' if is_u else 'av-bot'}"),
                html.Div([
                    html.Div(content_children,
                             className=f"bbl {'bbl-u' if is_u else 'bbl-bot'}"),
                ])
            ]
        ))
    return items

def _render_chunks(chunks: list):
    if not chunks:
        return html.Div(
            "Los fragmentos del corpus aparecerán aquí después de cada consulta.",
            style={"fontSize": "11px", "color": C["muted"], "lineHeight": "1.6"}
        )
    gcls = {"Rock": "g-rock", "Hip-Hop": "g-hip", "Metal": "g-metal"}
    cards = []
    for c in chunks[:4]:
        score_pct = int(c.get("score", 0) * 100)
        g = c.get("genre", "")
        cards.append(html.Div(className="chunk-card", children=[
            html.Div(className="chunk-top", children=[
                html.Span(f"Score {score_pct}%", className="chunk-score"),
                html.Span(g, className=f"gbadge {gcls.get(g, 'g-rock')}",
                          style={"fontSize": "10px", "padding": "3px 8px"}),
            ]),
            html.Div(f"🎵 {c.get('song','?')}  ·  {c.get('artist','?')}  ({c.get('year','?')})", className="chunk-meta"),
            html.Div(f"\"{c.get('texto','')[:220]}...\"", className="chunk-lyric"),
        ]))
    return cards

# ── Configuración UI y App ───────────────────────────────────────────────────

_ASSETS_DIR = os.path.join(PAGES_DIR, "assets")
os.makedirs(_ASSETS_DIR, exist_ok=True)
with open(os.path.join(_ASSETS_DIR, "musicbot.css"), "w", encoding="utf-8") as _f:
    _f.write(CSS)

app = dash.Dash(
    __name__,
    assets_folder=_ASSETS_DIR,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="MúsicBot",
)
server = app.server

app.layout = html.Div([
    dcc.Store(id="history",      data=[]),
    dcc.Store(id="chunks-store", data=[]),

    html.Div(id="shell", children=[
        html.Div(id="sidebar", children=[
            html.Div(id="sb-head", children=[
                html.Div("MúsicBot", className="logo"),
                html.Div("EXPERTO EN GÉNEROS", className="logo-tagline"),
            ]),
            html.Div(id="sb-body", children=[
                html.Div([
                    html.Div("Modelo LLM", className="sb-label"),
                    dcc.Dropdown(
                        id="model-dd",
                        options=[
                            {"label": "⚡  Gemini 2.5 Flash", "value": "gemini"},
                            {"label": "🔧  Flan-T5 Base (local)", "value": "flan"},
                        ],
                        value="gemini",
                        clearable=False,
                    ),
                ]),
                html.Div([
                    html.Div("Gemini API Key", className="sb-label"),
                    dcc.Input(
                        id="api-key", type="password", placeholder="AIza...", value=GEMINI_API_KEY, debounce=True, className="api-inp",
                    ),
                ]),

                html.Div([
                    dcc.Checklist(
                        id="use-rag-check",
                        options=[{"label": " Usar contexto RAG (Corpus)", "value": "rag"}],
                        value=["rag"],
                        style={"fontSize": "12px", "color": C["muted"], "cursor": "pointer"}
                    )
                ]),

                html.Button("🗑  Limpiar conversación", id="clear-btn", className="clear-btn", n_clicks=0),

                html.Button("💾  Exportar para Métricas",
                            id="export-btn", className="clear-btn", n_clicks=0,
                            style={"marginTop": "2px", "borderColor": C["accent"]+"66"}),
                dcc.Download(id="download-metrics"),

                html.Div(id="chunks-wrap", children=[
                    html.Div("Contexto RAG recuperado", className="sb-label"),
                    html.Div(id="chunks-inner", children=[
                        html.Div("Los fragmentos del corpus aparecerán aquí.", style={"fontSize":"11px","color":C["muted"],"lineHeight":"1.6"})
                    ]),
                ]),
            ]),
        ]),

        html.Div(id="main", children=[
            html.Div(id="chat-hdr", children=[
                html.Div(className="dot-live"),
                html.Div("MúsicBot", id="hdr-title"),
                html.Div("Rock · Hip-Hop · Metal", id="hdr-sub"),
                html.Div("GEMINI 2.5", id="model-badge"),
            ]),
            html.Div(id="msgs", children=[_welcome_screen()]),
            html.Div(id="inp-area", children=[
                html.Div(id="inp-row", children=[
                    dcc.Textarea(id="chat-inp", placeholder="Escribe sobre Rock, Hip-Hop o Metal...", value="", style={"height": "48px"}),
                    html.Button("➤", id="send-btn", n_clicks=0),
                ]),
                html.Div("Presiona el botón para enviar  ·  Solo respondo sobre música", className="hint"),
            ]),
        ]),
    ]),
])

# ══════════════════════════════════════════════════════════════════════════════
#  Callbacks
# ══════════════════════════════════════════════════════════════════════════════

@app.callback(
    Output("model-badge", "children"),
    Input("model-dd", "value"),
)
def _update_badge(model):
    return "GEMINI 2.5" if model == "gemini" else "FLAN-T5"

@app.callback(
    Output("chat-inp", "value", allow_duplicate=True),
    [Input("chip-1", "n_clicks"), Input("chip-2", "n_clicks"),
     Input("chip-3", "n_clicks"), Input("chip-4", "n_clicks")],
    prevent_initial_call=True,
)
def _fill_chip(*_):
    _map = {
        "chip-1": "¿Qué diferencia al Rock del Metal?",
        "chip-2": "Recomiéndame una canción de Hip-Hop",
        "chip-3": "¿Qué caracteriza el rap lírico?",
        "chip-4": "Canciones de Metal que hablen de libertad",
    }
    return _map.get(ctx.triggered_id, no_update)

@app.callback(
    Output("download-metrics", "data"),
    Input("export-btn", "n_clicks"),
    State("history", "data"),
    prevent_initial_call=True,
)
def _export_conversation(n_clicks, history):
    if not history:
        return no_update

    export_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": {
            "usuario": "Equipo Desarrollo",
            "modelo_utilizado": "Gemini 2.5 Flash / Flan-T5"
        },
        "conversacion": history,
        "evaluacion_sugerida": {
            "relevancia_rag": "1-5",
            "coherencia": "1-5",
            "alucinaciones": "No detectadas"
        }
    }

    return dict(
        content=json.dumps(export_data, indent=4, ensure_ascii=False),
        filename=f"conversacion_{datetime.now().strftime('%H%M%S')}.json"
    )

@app.callback(
    [Output("msgs",         "children"),
     Output("history",      "data"),
     Output("chunks-inner", "children"),
     Output("chat-inp",     "value")],
    [Input("send-btn",  "n_clicks"),
     Input("clear-btn", "n_clicks")],
    [State("chat-inp",  "value"),
     State("history",   "data"),
     State("model-dd",  "value"),
     State("api-key",   "value"),
     State("use-rag-check", "value")],
    prevent_initial_call=True,
)
def _on_action(send_n, clear_n, user_text, history, model, api_key, rag_check):
    triggered = ctx.triggered_id

    if triggered == "clear-btn":
        return [_welcome_screen()], [], _render_chunks([]), ""

    if not user_text or not user_text.strip():
        return no_update, no_update, no_update, no_update

    user_text = user_text.strip()
    history   = history or []
    history.append({"role": "user", "content": user_text})

    use_rag_flag = "rag" in (rag_check or [])

    answer, chunks = chatbot_respond(
        user_msg=user_text,
        history=history[:-1],
        model_choice=model,
        api_key=(api_key or GEMINI_API_KEY),
        use_rag=use_rag_flag
    )
    history.append({"role": "assistant", "content": answer})

    return _render_messages(history), history, _render_chunks(chunks), ""

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═"*54)
    print("   MúsicBot — Chatbot Musical Inteligente")
    print("       Rock · Hip-Hop · Metal")
    print("═"*54)
    print(f"\n  Raíz del proyecto : {PROJECT_ROOT}")

    _load_rag_index()
    _get_embed_model()
    if _load_classifier():
        print("[MúsicBot] ✓ Clasificador de género listo")

    print("─"*54)
    print("  ✅  Todo listo. Abriendo servidor...\n")
    print(f"  🌐  http://127.0.0.1:8050")

    app.run(debug=False, host="0.0.0.0", port=8050)