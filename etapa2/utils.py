import re
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer, WordNetLemmatizer

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("punkt_tab")


def drop_nans(df: pd.DataFrame):
    nans = df['textos'].isnull().sum()
    if nans > 0:
        print(f"Hay {nans} nulos")
        df.dropna(subset=['textos'], inplace=True)
        print("Nulos eliminados")

def drop_duplicates(df: pd.DataFrame):
    duplicates = df['textos'].duplicated().sum()
    if duplicates > 0:
        print(f"Hay {duplicates} duplicados")
        df.drop_duplicates(subset=['textos'], keep='first', inplace=True)
        print("Duplicados eliminados")
    pass

def drop_short_texts(df: pd.DataFrame, min_length: int = 300):
    temp_df = df.dropna(subset=['textos'])
    short_texts = temp_df[temp_df['textos'].str.len() < min_length]
    num_short_texts = len(short_texts)
    if num_short_texts > 0:
        print(f"Hay {num_short_texts} textos cortos (< {min_length} caracteres)")
        df.drop(short_texts.index, inplace=True)
        print("Textos cortos eliminados")
    pass

def limpiar_texto(texto):
    # 1. Minúsculas
    texto = texto.lower()
    
    # 2. Eliminar puntuación, números y caracteres especiales
    texto = re.sub(r"[^a-záéíóúñü\s]", "", texto)
    
    # 3. Tokenización
    tokens = word_tokenize(texto, language="spanish")
    
    # 4. Eliminar stopwords
    stop_words = set(stopwords.words("spanish"))
    tokens = [word for word in tokens if word not in stop_words]
    
    # 5. Normalización (ejemplo con stemming)
    stemmer = SnowballStemmer("spanish")
    tokens = [stemmer.stem(word) for word in tokens]
    
    # lematización:
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    return " ".join(tokens)

def clean_df(df: pd.DataFrame, use_nltk: bool = True) -> pd.DataFrame:
    df_ = df.copy()
    drop_nans(df_)
    drop_duplicates(df_)
    drop_short_texts(df_, min_length=300)
    df_['textos'] = df_['textos'].apply(limpiar_texto) if use_nltk else df_['textos']
    return df_
    pass