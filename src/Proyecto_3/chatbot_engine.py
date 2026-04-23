"""
chatbot_engine.py
─────────────────
Motor del chatbot: memoria conversacional, prompt, generación con Flan-T5.
"""

from transformers import pipeline as hf_pipeline
from src.Proyecto_3.rag_utils import buscar_chunks
from src.Proyecto_3.finetuning_utils import predecir_genero

GEN_MODEL    = "google/flan-t5-base"
MAX_HISTORIA = 5   # turnos de conversación a recordar

SYSTEM_PROMPT = """Eres GenreBot, un experto en géneros musicales. 
Conoces a fondo el Rock, Hip-Hop y Metal. 
Respondes preguntas sobre letras, artistas y géneros basándote ÚNICAMENTE en el corpus de canciones disponible.
Si no encuentras información relevante en el corpus, lo dices claramente.
Responde siempre en el mismo idioma en que te hacen la pregunta.
Sé conciso, preciso y útil."""

_generator = None


def _get_generator():
    def _get_generator():
        global _generator
        if _generator is None:
            try:
                print("Cargando generador GPT-2...")
                _generator = hf_pipeline(
                    "text-generation",
                    model="gpt2",
                    max_new_tokens=128,
                )
                print("Generador listo.")
            except Exception as e:
                print(f"Error cargando generador: {e}")
                return None
        return _generator

    _generator = hf_pipeline(
        "text-generation",
        model="gpt2",
        max_new_tokens=128,
    )

def construir_prompt(pregunta, chunks, historial):
    """
    Ensambla el prompt con: sistema + historial + contexto RAG + pregunta.
    """
    contexto = "\n\n".join([
        f"[{c['song']} - {c['artist']} ({c['genre']}, {c['year']})]\n{c['texto'][:300]}"
        for c in chunks
    ])

    hist_txt = ""
    for turno in historial[-MAX_HISTORIA:]:
        hist_txt += f"Usuario: {turno['usuario']}\nGenreBot: {turno['bot']}\n"

    prompt = f"""{SYSTEM_PROMPT}

--- HISTORIAL ---
{hist_txt}

--- CONTEXTO DEL CORPUS ---
{contexto}

--- PREGUNTA ACTUAL ---
{pregunta}

--- RESPUESTA ---"""
    return prompt


class ChatbotMusical:
    def __init__(self):
        self.historial = []

    def responder(self, pregunta):
        # 1. Detectar género mencionado
        pregunta_lower = pregunta.lower()
        filtro = None
        for g, variantes in [("Rock", ["rock"]), ("Hip-Hop", ["hip-hop", "hip hop"]), ("Metal", ["metal"])]:
            if any(v in pregunta_lower for v in variantes):
                filtro = g
                break

        # 2. Buscar chunks relevantes
        try:
            chunks = buscar_chunks(pregunta, top_k=5, filtro_genero=filtro)
            if not chunks:
                chunks = buscar_chunks(pregunta, top_k=5)
        except RuntimeError:
            return "El sistema RAG aún no está inicializado."

        if not chunks:
            return "No encontré información relevante en el corpus para tu pregunta."

        # 3. Construir respuesta directamente desde el corpus
        respuesta = f"Basándome en el corpus, encontré estas canciones relevantes:\n\n"
        for i, c in enumerate(chunks[:3], 1):
            respuesta += f"**{i}. {c['song']}** — {c['artist']} ({c['genre']}, {c['year']})\n"
            respuesta += f"{c['texto'][:200]}...\n\n"

        # Fuentes
        fuentes = list({f"{c['song']} — {c['artist']} ({c['genre']})" for c in chunks[:3]})
        respuesta += "📀 *Fuentes del corpus:*\n" + "\n".join(f"• {f}" for f in fuentes)

        # 4. Guardar en historial
        self.historial.append({"usuario": pregunta, "bot": respuesta})
        return respuesta

    def limpiar_historial(self):
        self.historial = []
        return "Historial limpiado."

    def get_historial(self):
        return self.historial
