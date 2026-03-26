# setup.py
# Ejecutar UNA VEZ desde la raíz del proyecto:
#   pip install -e .
# Esto hace que 'src' sea importable desde cualquier notebook
# sin necesidad de manipular sys.path manualmente.

from setuptools import setup, find_packages

setup(
    name="proyecto2-semantico",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "langdetect",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "scipy",
        "gensim",
        "transformers",
        "torch",
    ],
)
