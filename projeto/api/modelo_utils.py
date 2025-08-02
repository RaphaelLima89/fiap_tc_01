import os
import joblib
import pandas as pd
from pydantic import BaseModel
from typing import List

# Carregando o modelo e o encoder
path_model = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "modelo_bookscrape.pkl")
)
path_encoder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "encoder.pkl")
)

try:
    modelo = joblib.load(path_model)
    encoder = joblib.load(path_encoder)
except Exception as e:
    raise RuntimeError(f"Erro ao carregaro modelo/encoder: {e}")

# Classes de entrada


class LivroInput(BaseModel):
    preco_incl_tax: float
    disponibilidade_produto: int
    qtde_estrelas: int


class EntradaModelo(BaseModel):
    itens: List[LivroInput]


# Função para prever a categoria
def prever_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe um dataframe e retorna com os valores previstos
    """

    features = ["qtde_estrelas", "preco_incl_tax", "disponibilidade_produto"]

    try:
        df_filtrado = df[features]
    except KeyError:
        raise ValueError("As colunas não estão no formato esperado")

    y_pred = modelo.predict(df_filtrado)
    categorias = encoder.inverse_transform(y_pred)

    df_resultado = df_filtrado.copy()
    df_resultado["predicao"] = categorias
    return df_resultado
