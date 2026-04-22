"""
finetuning_utils.py
───────────────────
Dataset, entrenamiento y evaluación del clasificador de género.
Modelo base: distilbert-base-multilingual-cased (viable en CPU).
"""

import os
import json
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODEL_BASE = "distilbert-base-multilingual-cased"
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "..", "models", "clasificador_genero")
LABEL_FILE = os.path.join(MODEL_DIR, "label_encoder.json")

GENEROS_TARGET = ["Rock", "Hip-Hop", "Metal"]
SEED = 42


# ── Preparación del dataset ───────────────────────────────────────────────────
def preparar_dataset(df, text_col="Lyrics", label_col="Genre", max_len=256):
    """
    Filtra el df a los géneros objetivo, codifica etiquetas y
    divide en train/val/test (70/15/15).
    """
    from transformers import AutoTokenizer
    from datasets import Dataset
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder

    # 1. Filtrado y limpieza
    df_filtrado = df[df[label_col].isin(GENEROS_TARGET)].copy()
    df_filtrado = df_filtrado[[text_col, label_col]].dropna()
    # Limitar texto para evitar problemas de memoria
    df_filtrado[text_col] = df_filtrado[text_col].astype(str).str[:512]

    # 2. Codificación de etiquetas
    le = LabelEncoder()
    df_filtrado["label"] = le.fit_transform(df_filtrado[label_col])

    # Guardar mapping de etiquetas
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(LABEL_FILE, "w") as f:
        json.dump({"classes": le.classes_.tolist()}, f)

    # 3. División del dataset
    X = df_filtrado[text_col]
    y = df_filtrado["label"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    print(f"Clases: {le.classes_.tolist()}")

    # 4. Cargar el Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE)

    # 5. Función interna de tokenización corregida
    def aplicar_tokenizacion(textos, etiquetas):
        # Convertimos a lista para el tokenizer
        textos_lista = textos.tolist() if hasattr(textos, 'tolist') else textos
        etiquetas_lista = etiquetas.tolist() if hasattr(etiquetas, 'tolist') else etiquetas

        # CAMBIO CLAVE: Usamos el objeto 'tokenizer', no el nombre de la función
        enc = tokenizer(
            textos_lista,
            padding=True,
            truncation=True,
            max_length=max_len,
            return_tensors=None
        )

        return Dataset.from_dict({
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": etiquetas_lista,
        })

    # 6. Retornar los datasets procesados llamando a la función corregida
    return (
        aplicar_tokenizacion(X_train, y_train),
        aplicar_tokenizacion(X_val, y_val),
        aplicar_tokenizacion(X_test, y_test),
        le
    )




# ── Entrenamiento ─────────────────────────────────────────────────────────────

def entrenar_clasificador(ds_train, ds_val, num_labels, num_epochs=3):
    """
    Fine-tuning de DistilBERT para clasificación de género.
    """
    from transformers import (AutoModelForSequenceClassification,
                              TrainingArguments, Trainer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_BASE, num_labels=num_labels)

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(labels, preds),
            "f1_macro": f1_score(labels, preds, average="macro"),
        }

    # Busca esta sección en finetuning_utils.py (alrededor de la línea 119)
    args = TrainingArguments(
        output_dir=MODEL_DIR,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",  # <--- CAMBIA 'evaluation_strategy' por 'eval_strategy'
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        logging_steps=50,
        seed=SEED,
        # no_cuda=True,             # Nota: no_cuda también está marcado como obsoleto en versiones nuevas
        use_cpu=True,  # <--- CAMBIO RECOMENDADO: Usa 'use_cpu=True' en lugar de 'no_cuda=True'
        report_to="none",
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds_train,
        eval_dataset=ds_val,
        compute_metrics=compute_metrics,
    )

    print("Iniciando fine-tuning...")
    trainer.train()
    trainer.save_model(MODEL_DIR)
    print(f"Modelo guardado en {MODEL_DIR}")
    return trainer, model


# ── Evaluación ────────────────────────────────────────────────────────────────

def evaluar_modelo(trainer, ds_test, le):
    """Evalúa sobre el conjunto de test y retorna métricas."""
    pred_output = trainer.predict(ds_test)
    preds  = np.argmax(pred_output.predictions, axis=-1)
    labels = pred_output.label_ids

    acc  = accuracy_score(labels, preds)
    f1   = f1_score(labels, preds, average="macro")
    cm   = confusion_matrix(labels, preds)

    print(f"\nTest Accuracy : {acc:.4f}")
    print(f"Test F1 Macro : {f1:.4f}")
    print(f"Clases        : {le.classes_.tolist()}")
    print(f"Matriz de confusión:\n{cm}")

    return {"accuracy": acc, "f1_macro": f1,
            "confusion_matrix": cm.tolist(),
            "classes": le.classes_.tolist()}


# ── Inferencia ────────────────────────────────────────────────────────────────

_clf_model     = None
_clf_tokenizer = None
_clf_le        = None


def cargar_clasificador():
    global _clf_model, _clf_tokenizer, _clf_le
    if _clf_model is None:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        _clf_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        _clf_model     = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        _clf_model.eval()
        with open(LABEL_FILE) as f:
            _clf_le = json.load(f)["classes"]
    return _clf_model, _clf_tokenizer, _clf_le


def predecir_genero(texto):
    """Predice el género de un texto dado."""
    import torch
    model, tokenizer, clases = cargar_clasificador()
    enc = tokenizer(texto[:512], return_tensors="pt",
                    truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        logits = model(**enc).logits
    idx = logits.argmax(-1).item()
    return clases[idx]
