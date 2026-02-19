# An-lisis-Morfosint-ctico-de-Letras-Musicales

# Descripción 
Este proyecto tiene como objetivo realizar un análisis lingüístico de las letras de canciones. Por medio de técnicas de procesamiento del lenguaje natural (PLN), llevamos a cabo un análisis morfosintáctico (con etiquetado POS y tokenización) para identificar patrones estilísticos, el uso de categorías gramaticales y otras características del texto lírico.

Además, se realizó una comparación entre los géneros musicales que conforman el corpus lingüístico utilizado, en conjunto con un análisis de evolución temporal del corpus, dividido por décadas, desde la década de 1970 hasta la década de 2010.

# Características principales

Extracción y limpieza de letras: Procesamiento de datos crudos (ej. lyrics_clean.csv) para su análisis.

Análisis morfosintáctico: Implementación de pipelines con librerías como spaCy (ver notebooks/ y src/).

Visualización interactiva: Dashboard para explorar los resultados (carpeta dashboard/).

Código modular: Scripts organizados en src/ y utilidades en scripts/ para facilitar su reutilización.

Uso responsable de IA: Documentación del proceso y herramientas de IA empleadas en USO_DE_IA.md.


# Estructura del proyecto

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
