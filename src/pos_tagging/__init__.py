#Llamar variables
from .Taggin_spacy import apply_pos_tagging_spacy
from .nltk_tagger import apply_pos_tagging_nltk
from .comparator import comparar_nltk_spacy_csv
__all__ = ["apply_pos_tagging_nltk", "apply_pos_tagging_spacy","comparar_nltk_spacy_csv"]



