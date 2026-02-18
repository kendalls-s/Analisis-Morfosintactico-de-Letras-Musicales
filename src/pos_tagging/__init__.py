#Llamar variables
from .Taggin_spacy import apply_pos_tagging_spacy
from .nltk_tagger import apply_pos_tagging
__all__ = ["apply_pos_tagging", "apply_pos_tagging_spacy"]



