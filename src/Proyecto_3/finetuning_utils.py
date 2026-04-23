"""
finetuning_utils.py
───────────────────
Dataset, baseline Zero-Shot, entrenamiento, evaluación e inferencia del clasificador.
Modelo base: distilbert-base-multilingual-cased.
"""

import os
import json
import numpy as np

os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODEL_BASE = "distilbert-base-multilingual-cased"
MODEL_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "clasificador_genero"))
LABEL_FILE = os.path.join(MODEL_DIR, "label_encoder.json")
RESULTADOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "resultados"))

GENEROS_TARGET = ["Rock", "Hip-Hop", "Metal"]
SEED = 42

# ── 1. Preparación del Dataset ────────────────────────────────────────────────
def preparar_dataset(df, text_col="Lyrics", label_col="Genre", max_len=256):
    """Filtra géneros, codifica etiquetas y divide en train/val/test."""
    from transformers import AutoTokenizer
    from datasets import Dataset
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder

    df_filtrado = df[df[label_col].isin(GENEROS_TARGET)].copy()
    df_filtrado = df_filtrado[[text_col, label_col]].dropna()
    df_filtrado[text_col] = df_filtrado[text_col].astype(str).str[:512]

    le = LabelEncoder()
    df_filtrado["label"] = le.fit_transform(df_filtrado[label_col])

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(LABEL_FILE, "w") as f:
        json.dump({"classes": le.classes_.tolist()}, f)

    X = df_filtrado[text_col]
    y = df_filtrado["label"]

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=SEED, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=SEED, stratify=y_temp)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE)

    def aplicar_tokenizacion(textos, etiquetas):
        textos_lista = textos.tolist() if hasattr(textos, 'tolist') else textos
        etiquetas_lista = etiquetas.tolist() if hasattr(etiquetas, 'tolist') else etiquetas
        enc = tokenizer(textos_lista, padding=True, truncation=True, max_length=max_len, return_tensors=None)
        return Dataset.from_dict({
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": etiquetas_lista,
        })

    return (
        aplicar_tokenizacion(X_train, y_train),
        aplicar_tokenizacion(X_val, y_val),
        aplicar_tokenizacion(X_test, y_test),
        le,
        df_filtrado # Retornamos el df limpio para el Zero-Shot
    )

# ── 2. Baseline Zero-Shot ─────────────────────────────────────────────────────
def evaluar_zero_shot(df_target, text_col="Lyrics", label_col="Genre", sample_size=100):
    """Evalúa el modelo preentrenado sin fine-tuning para establecer un baseline."""
    from transformers import pipeline
    from sklearn.metrics import accuracy_score, f1_score
    import time

    print(f"\n⚙ Calculando Baseline Zero-Shot con {sample_size} muestras aleatorias...")
    t0 = time.time()

    zs_pipeline = pipeline('zero-shot-classification', model=MODEL_BASE, device=-1)
    muestra = df_target.sample(sample_size, random_state=SEED)

    preds_zs = []
    textos = muestra[text_col].astype(str).str[:300].tolist()

    for res in zs_pipeline(textos, candidate_labels=GENEROS_TARGET):
        preds_zs.append(res['labels'][0])

    labels_true = muestra[label_col].tolist()

    acc = accuracy_score(labels_true, preds_zs)
    f1 = f1_score(labels_true, preds_zs, average='macro', zero_division=0)

    print(f"  ✓ Zero-Shot completado en {time.time()-t0:.1f}s")
    print(f"  → Accuracy Zero-Shot: {acc:.4f} | F1 Macro: {f1:.4f}")

    return acc, f1

# ── 3. Entrenamiento ──────────────────────────────────────────────────────────
def entrenar_clasificador(ds_train, ds_val, num_labels, num_epochs=3):
    """Fine-tuning del modelo base."""
    from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
    from sklearn.metrics import accuracy_score, f1_score

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_BASE, num_labels=num_labels)

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(labels, preds),
            "f1_macro": f1_score(labels, preds, average="macro"),
        }

    args = TrainingArguments(
        output_dir=MODEL_DIR,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        logging_steps=50,
        seed=SEED,
        use_cpu=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds_train,
        eval_dataset=ds_val,
        compute_metrics=compute_metrics,
    )

    print("\n Iniciando fine-tuning...")
    trainer.train()
    trainer.save_model(MODEL_DIR)
    print(f"✓ Modelo guardado en {MODEL_DIR}")
    return trainer, model

# ── 4. Evaluación y Gráficos ──────────────────────────────────────────────────
def evaluar_y_guardar(trainer, ds_test, le, acc_zs=None, f1_zs=None):
    """Evalúa test, imprime comparación vs Zero-Shot, guarda matriz y JSON."""
    from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    pred_output = trainer.predict(ds_test)
    preds  = np.argmax(pred_output.predictions, axis=-1)
    labels = pred_output.label_ids

    acc  = accuracy_score(labels, preds)
    f1   = f1_score(labels, preds, average="macro")
    cm   = confusion_matrix(labels, preds)
    clases = le.classes_.tolist()

    print(f"\n{'='*40}\nCOMPARACIÓN FINAL\n{'='*40}")
    if acc_zs is not None:
        print(f"Zero-Shot  — Accuracy: {acc_zs:.4f} | F1: {f1_zs:.4f}")
    print(f"Fine-Tuned — Accuracy: {acc:.4f} | F1: {f1:.4f}")

    if acc_zs is not None:
        print(f"Ganancia   — Accuracy: +{acc - acc_zs:.4f} | F1: +{f1 - f1_zs:.4f}")
    print('='*40)

    # Guardar métricas en JSON
    os.makedirs(RESULTADOS_DIR, exist_ok=True)
    metricas = {
        "accuracy": acc, "f1_macro": f1,
        "zero_shot_accuracy": acc_zs, "zero_shot_f1": f1_zs,
        "confusion_matrix": cm.tolist(), "classes": clases
    }
    with open(os.path.join(RESULTADOS_DIR, 'metricas.json'), 'w', encoding='utf-8') as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)

    # Generar y guardar Matriz de Confusión
    fig, ax = plt.subplots(figsize=(7, 5))
    disp = ConfusionMatrixDisplay(cm, display_labels=clases)
    disp.plot(ax=ax, cmap='Blues', colorbar=False)
    ax.set_title('Matriz de Confusión — Clasificador Fine-Tuneado')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTADOS_DIR, 'confusion_matrix.png'), dpi=150)
    plt.show()

    print(f"\n✓ Métricas y gráfico guardados en la carpeta 'resultados'.")
    return metricas

# ── 5. Inferencia (Chatbot) ───────────────────────────────────────────────────
_clf_model, _clf_tokenizer, _clf_le = None, None, None

def cargar_clasificador():
    global _clf_model, _clf_tokenizer, _clf_le
    if _clf_model is None:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        _clf_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        _clf_model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        _clf_model.eval()
        with open(LABEL_FILE) as f:
            _clf_le = json.load(f)["classes"]
    return _clf_model, _clf_tokenizer, _clf_le

def predecir_genero(texto):
    import torch
    model, tokenizer, clases = cargar_clasificador()
    enc = tokenizer(texto[:512], return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        logits = model(**enc).logits
    return clases[logits.argmax(-1).item()]

def ejecutar_pruebas_inferencia(ejemplos):
    print("\n Pruebas de Inferencia Rápidas:")
    for e in ejemplos:
        print(f"  Texto: \"{e[:60]}...\" \n  → Predicción: {predecir_genero(e)}\n")