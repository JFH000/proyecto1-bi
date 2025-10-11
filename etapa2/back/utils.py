import re
import pandas as pd

# NLTK: carga perezosa y robusta
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer, WordNetLemmatizer

def _ensure_nltk():
    """Verifica y descarga recursos necesarios (idempotente)."""
    # punkt (modelo) y punkt_tab (tablas) — algunas versiones usan ambos
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        # En versiones viejas no existe; si falla, no es crítico gracias a preserve_line=True
        try:
            nltk.download("punkt_tab", quiet=True)
        except Exception:
            pass
    # stopwords y wordnet
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet", quiet=True)

def drop_nans(df: pd.DataFrame):
    nans = df["textos"].isnull().sum()
    if nans > 0:
        print(f"Hay {nans} nulos")
        df.dropna(subset=["textos"], inplace=True)
        print("Nulos eliminados")

def drop_duplicates(df: pd.DataFrame):
    duplicates = df["textos"].duplicated().sum()
    if duplicates > 0:
        print(f"Hay {duplicates} duplicados")
        df.drop_duplicates(subset=["textos"], keep="first", inplace=True)
        print("Duplicados eliminados")

def drop_short_texts(df: pd.DataFrame, min_length: int = 300):
    temp_df = df.dropna(subset=["textos"])
    short_texts = temp_df[temp_df["textos"].str.len() < min_length]
    num_short_texts = len(short_texts)
    if num_short_texts > 0:
        print(f"Hay {num_short_texts} textos cortos (< {min_length} caracteres)")
        df.drop(short_texts.index, inplace=True)
        print("Textos cortos eliminados")

def limpiar_texto(texto: str) -> str:
    """
    Limpieza reproducible:
    - lower
    - quitar signos/números
    - tokenizar (evitando sent_tokenize con preserve_line=True)
    - quitar stopwords (es)
    - stemming Snowball (es)
    - lematizar (WordNet; si no aplica en es, no afecta)
    Con fallbacks si faltan recursos.
    """
    if texto is None:
        return ""
    texto = str(texto).lower()
    texto = re.sub(r"[^a-záéíóúñü\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    # Tokenización robusta
    tokens = []
    try:
        _ensure_nltk()
        # preserve_line=True evita sent_tokenize -> no requiere punkt/punkt_tab
        tokens = word_tokenize(texto, language="spanish", preserve_line=True)
    except Exception:
        # Fallback sin NLTK
        tokens = texto.split()

    # Stopwords
    try:
        sw = set(stopwords.words("spanish"))
        tokens = [w for w in tokens if w not in sw]
    except LookupError:
        pass

    # Stemming
    try:
        stemmer = SnowballStemmer("spanish")
        tokens = [stemmer.stem(w) for w in tokens]
    except Exception:
        pass

    # Lemmatization (WordNet mayormente en inglés; si no aporta, no rompe)
    try:
        lem = WordNetLemmatizer()
        tokens = [lem.lemmatize(w) for w in tokens]
    except Exception:
        pass

    return " ".join(tokens)

def clean_df(df: pd.DataFrame, use_nltk: bool = True, use_short_text: bool = False) -> pd.DataFrame:
    """
    - Si use_short_text=False: elimina < 300 chars (para entrenamiento).
    - Si use_short_text=True: NO elimina cortos (para predicción).
    """
    df_ = df.copy()
    drop_nans(df_)
    drop_duplicates(df_)
    if not use_short_text:
        drop_short_texts(df_, min_length=300)
    if use_nltk:
        df_["textos"] = df_["textos"].apply(limpiar_texto)
    return df_
