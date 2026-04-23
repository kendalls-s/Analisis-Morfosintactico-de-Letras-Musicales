# Proyecto #1  An-lisis-Morfosint-ctico-de-Letras-Musicales - Proyecto 2 Analisis Semantico de letras musicales - Proyecto #3 — Chatbot Musical Inteligente: Agente Conversacional con RAG y Fine-Tuning

# Descripción 
Este proyecto tiene como objetivo realizar un análisis lingüístico de las letras de canciones. Por medio de técnicas de procesamiento del lenguaje natural (PLN), llevamos a cabo un análisis morfosintáctico (con etiquetado POS y tokenización) para identificar patrones estilísticos, el uso de categorías gramaticales y otras características del texto lírico.

Además, se realizó una comparación entre los géneros musicales que conforman el corpus lingüístico utilizado, en conjunto con un análisis de evolución temporal del corpus, dividido por décadas, desde la década de 1970 hasta la década de 2010.


Sumado a esto, el proyecto 2 consiste en aplicar técnicas de representación semántica (Word2Vec y BETO) para analizar las relaciones de significado en letras musicales, integrando un pipeline completo que incluya Web Scraping para enriquecimiento del corpus, almacenamiento en MongoDB, y comparación de representaciones vectoriales estáticas vs. contextuales entre géneros musicales.

Este tercer y último proyecto integra todo lo aprendido durante el cuatrimestre sobre el mismo corpus de letras de canciones trabajado desde el Proyecto 1. Partiendo del análisis morfosintáctico (Proyecto 1) y las representaciones vectoriales densas (Proyecto 2), el reto final es construir un agente conversacional funcional — un chatbot musical — que utilice Retrieval-Augmented Generation (RAG), un clasificador obtenido por fine-tuning, y una interfaz web con Plotly Dash para que cualquier usuario pueda interactuar con el sistema.

El chatbot responde preguntas sobre música, letras, artistas y géneros, fundamentando sus respuestas en el corpus real de canciones. Por debajo, pone en práctica los conceptos más importantes del PLN moderno: modelos preentrenados, fine-tuning, embeddings contextualizados, búsqueda semántica y generación de lenguaje natural.

# Características principales

Extracción y limpieza de letras: Procesamiento de datos crudos (ej. lyrics_clean.csv) para su análisis.

Análisis morfosintáctico: Implementación de pipelines con librerías como spaCy (ver notebooks/ y src/).

Visualización interactiva: Dashboard para explorar los resultados (carpeta dashboard/).

Código modular: Scripts organizados en src/ y utilidades en scripts/ para facilitar su reutilización.

Web Scraping y Enriquecimiento del Corpus: el cual implemenea un scraper funcional que extraiga letras musicales de al menos un sitio web

Almacenamiento NoSQL con MongoDB: el cual diseña un esquema documental apropiado para el corpus musical, migrar los datos del Proyecto 1, e integrar los nuevos datos del scraping en una base de datos MongoDB

Dominio de Word2Vec: El cual entrena modelos Word2Vec (CBOW y Skip-Gram) sobre el corpus musical para descubrir campos semánticos, realizar analogías vectoriales y comparar representaciones entre géneros musicales

Embelding contextuales con BERT: desde HuggingFace para generar embeddings contextuales, demostrando cómo una misma palabra adquiere representaciones distintas según el contexto y género musical.

Comparación BoW vs. Word2Vec vs. BETO: Realizar una comparación sistemática de las tres representaciones (dispersa, estática densa, contextual densa) evaluando cuál captura mejor las diferencias semánticas entre géneros musicales.

Pipeline RAG completo: Chunking de letras de canciones con preservación de metadatos, generación de embeddings multilingüe con sentence-transformers, indexación vectorial con FAISS y recuperación semántica para generar respuestas contextualizadas fundamentadas en el corpus.

Clasificador por Fine-Tuning: Entrenamiento supervisado de un modelo Transformer preentrenado (BETO, DistilBERT o Electra) especializado en la tarea de clasificación elegida por el equipo (género, emoción o época).

Agente conversacional con memoria: El chatbot mantiene un historial de los últimos N turnos (mínimo 5) que le permite entender preguntas de seguimiento como "Dame otra del mismo género" 

Interfaz web con Plotly Dash: Aplicación lanzable con un solo comando que permite a usuarios no técnicos interactuar con el sistema directamente desde el navegador

Personalidad coherente del chatbot: El chatbot tiene un dominio y carácter definidos según la línea de investigación elegida (Experto en géneros, Curador emocional o Historiador musical)



Uso responsable de IA: Documentación del proceso y herramientas de IA empleadas en USO_DE_IA.md.




# Estructura del proyecto # 1 

├── data/               # Datos crudos y procesados (ej. lyrics_clean.csv)

├── notebooks/          # Jupyter notebooks para experimentación y análisis

├── src/                # Código fuente principal (módulos de análisis)

├── scripts/            # Scripts de utilidad y automatización

├── dashboard/          # Aplicación de visualización (si aplica)

├── outputs/            # Resultados, gráficos y tablas generadas

├── tests/              # Pruebas unitarias

├── docs/               # Documentación adicional

├── requirements.txt    # Dependencias del proyecto

├── USO_DE_IA.md        # Declaración de uso de inteligencia artificial

└── README.md           # Este archivo


# Estructura del proyecto # 2
├── README.md

├── USO_DE_IA.md

├── requirements.txt

├── notebooks/

│   ├── 01_migracion_mongodb.ipynb

│   ├── 02_web_scraping.ipynb

│   ├── 03_word2vec_analisis.ipynb

│   ├── 04_beto_analisis.ipynb

│   └── 05_comparacion_final.ipynb

├── src/

│   ├── db_manager.py          # Conexión y operaciones MongoDB

│   ├── scraper.py             # Web scraping de letras

│   ├── preprocessing.py       # Limpieza y tokenización

│   ├── embeddings_w2v.py      # Funciones Word2Vec

│   └── embeddings_beto.py     # Funciones BETO

├── dashboard/

│   └── app.py                 # Dashboard con Plotly Dash

├── data/

│   └── raw/                   # CSVs originales del Proyecto 1

└── docs/
    └── esquema_mongodb.md     # Documentación del esquema


# Estructura del proyecto # 3

├── notebooks/
│   ├── 01_exploracion_corpus.ipynb        # Estadísticas del dataset
│   ├── 02_rag_pipeline.ipynb              # Chunking + embeddings + FAISS + generador
│   ├── 03_finetuning_clasificador.ipynb   # Entrenamiento del modelo especializado
│   └── 04_chatbot_completo.ipynb          # Chatbot integrado (pruebas en notebook)


├── app/
│   ├── chatbot_app.py                     # Aplicación Plotly Dash (punto de entrada)
│   └── config.py                          # Variables de entorno, rutas, API keys


├── src/
│   ├── rag_utils.py                       # Chunking, embeddings, FAISS, búsqueda
│   ├── finetuning_utils.py                # Dataset, Trainer, evaluación
│   └── chatbot_engine.py                  # Clase del chatbot (memoria, prompt, generación)
│
├── data/
│   ├── corpus_canciones.csv               # El mismo dataset de proyectos 1 y 2
│   └── embeddings_cache/                  # Embeddings pre-calculados (numpy o pickle)


├── models/                                # Modelo fine-tuneado guardado
├── resultados/                            # Métricas, matrices de confusión, logs
├── requirements.txt                       # Dependencias del proyecto
├── USO_DE_IA.md                           # Declaración de uso de inteligencia artificial
└── README.md                              # Este archivo



# Tecnologías utilizadas

Lenguajes: Python 

Librerías principales: spaCy, pandas, numpy, matplotlib/seaborn, transformers, sickit-learn, torch, gensim (inferido del contexto)

Herramientas: Git, MongoDB, Google Colab (GPU T4 para fine-tuning), Hugging Face Hub, entornos virtuales

# Contribuidores

Kendall Solano Solís 

Roberto Coto Guevara 
