import os
from fastapi import FastAPI
from fastapi import HTTPException
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from typing import Optional
from . import auth
from .auth import get_current_user
from fastapi import Depends
from sklearn.model_selection import train_test_split
from .modelo_utils import EntradaModelo, prever_categoria
from .log_config import configurar_logger
from fastapi import Request
import time

# Inicializando o FastAPI

app = FastAPI(
    title="API Pública para Consulta de Livros",
    version="1.0.0",
    description="API para consulta de livros do site Book to Scrape, categorias e detalhes de livros.",
)

# Chamando o Logging
logger = configurar_logger()


# Utilizado o middleware para ativar o log de todas as requisições
@app.middleware("http")
async def log_requisicoes(request: Request, call_next):
    inicio = time.time()
    resposta = await call_next(request)
    duracao = round(time.time() - inicio, 4)
    client_ip = request.client.host

    logger.info(
        f'ip="{client_ip}", endpoint="{request.url.path}", method="{request.method}", status_code={resposta.status_code}, exec_time={duracao}s'
    )

    return resposta


app.include_router(auth.router)


def carregar_dataframe():
    """
    Função que carrega o DataFrame de livros a partir de um arquivo CSV.
    """

    path_csv = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path_csv = os.path.join(path_csv, "data", "books_dataset.csv")

    if not os.path.exists(path_csv):
        print("Arquivo CSV não encontrada. Tente rodar novamente o script de raspagem.")
        return DataFrame()
    df_livros = read_csv(path_csv, encoding="utf-8", header=0, sep=";")
    return df_livros


# Endpoints Core


@app.get("/api/v1/books", tags=["Core"])
def listar_livros():
    """
    Endpoint para listar todos os livros disponíveis.
    """
    df_livros = carregar_dataframe()
    if df_livros.empty:
        return {"message": "Nenhum livro encontrado."}
    return df_livros.to_dict(orient="records")


@app.get("/api/v1/books/search", tags=["Core"])
def buscar_livros(titulo: Optional[str] = None, categoria: Optional[str] = None):
    """
    Endpoint para buscar livros por título e/ou categoria.
    """

    df_livros = carregar_dataframe()

    selecao = df_livros.copy()

    if titulo is not None and titulo != "":
        selecao = selecao[selecao["titulo"].str.contains(titulo, case=False, na=False)]
    if categoria is not None and categoria != "":
        selecao = selecao[
            selecao["categoria"].str.contains(categoria, case=False, na=False)
        ]

    if selecao.empty:
        raise HTTPException(status_code=404, detail="Busca não retornou nenhum livro.")

    return selecao.to_dict(orient="records")


@app.get("/api/v1/categories", tags=["Core"])
def listar_categorias():
    """
    Endpoint para listar as categorias que estão disponíveis no dataset.
    """

    df_livros = carregar_dataframe()
    lista_categorias = df_livros["categoria"].unique().tolist()
    if not lista_categorias:
        raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada.")
    return {"categorias": lista_categorias}


@app.get("/api/v1/health", tags=["Core"])
def health_check():
    """
    Endpoint para verificar a saúde da API.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(
            status_code=500,
            detail="API online, mas o dataset não pôde ser carregado corretamente.",
        )

    return {"status": "API online e dataset carregado."}


# Endpoints de Insights


@app.get("/api/v1/stats/overview", tags=["Insights"])
def stats_overview():
    """
    Endpoint para obter uma visão geral dos dados.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Estatísticas não disponíveis.")

    total_livros = len(df_livros)
    preco_medio = df_livros["preco_incl_tax"].mean()
    distribuicao_rating = (
        df_livros["qtde_estrelas"].value_counts().sort_index().to_dict()
    )

    return {
        "total_livros": total_livros,
        "preco_medio": preco_medio,
        "distribuicao_rating": distribuicao_rating,
    }


@app.get("/api/v1/stats/categories", tags=["Insights"])
def stats_categories():
    """
    Endpoint com as estatísitcas por categoria.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(
            status_code=404, detail="Estatísticas por categoria não disponíveis."
        )

    stats_categories = df_livros.groupby("categoria").agg(
        total_livros=("id", "count"),
        preco_medio=("preco_incl_tax", "mean"),
        rating_medio=("qtde_estrelas", "mean"),
    )

    stats_categories = stats_categories.reset_index().to_dict(orient="records")
    return {"stats_categories": stats_categories}


@app.get("/api/v1/books/top-rated", tags=["Insights"])
def top_rated_books(top: Optional[int] = 50):
    """
    Endpoint para obter os livros mais bem avaliados.
    Observar que a consulta não é determinística, ou seja, a cada execução pode retornar livros diferentes.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Dados não disponíveis.")
    top_rated = df_livros.nlargest(top, "qtde_estrelas")
    colunas_filtradas = ["id", "categoria", "titulo", "qtde_estrelas"]
    top_rated = top_rated[colunas_filtradas]

    return top_rated.to_dict(orient="records")


@app.get("/api/v1/books/price-range", tags=["Insights"])
def stats_price_range(min: float, max: float):
    """
    Endpoint para obter os livros dentro de um intervalo de preço.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Dados não disponíveis.")

    selecao = df_livros[
        (df_livros["preco_incl_tax"] >= min) & (df_livros["preco_incl_tax"] <= max)
    ]

    colunas_filtradas = ["id", "categoria", "titulo", "preco_incl_tax", "qtde_estrelas"]
    selecao = selecao[colunas_filtradas]

    if selecao.empty:
        raise HTTPException(
            status_code=404, detail="Nenhum livro encontrado nesse intervalo de preço."
        )

    return selecao.to_dict(orient="records")


@app.get("/api/v1/books/{id_livro}", tags=["Core"])
def retorna_livro_por_id(id_livro: int):
    """
    Endpoint para retornar livro específico pelo ID.
    """

    df_livros = carregar_dataframe()
    livro_selecionado = df_livros[df_livros["id"] == id_livro]
    if livro_selecionado.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    return livro_selecionado.to_dict(orient="records")[0]


# Desafio 1: Endpoints com Autenticação


@app.get("/api/v1/scraping/trigger", tags=["Authentication"])
def scraping_trigger(user: str = Depends(get_current_user)):
    """
    Endpoint para acionar o scraping de livros.
    Necessário autenticação JWT.
    """
    return {"message": "Scraping acionado com sucesso."}


# Desafio 2: Pipeline ML-Ready


@app.get("/api/v1/ml/features", tags=["ML-Ready"])
def ml_features():
    """
    Endpoint para retornar as features utilizadas no modelo de Machine Learning.
    Para ajudar na inspeção dos dados, serão retornados os tipos de dados, informações estatísticas e as primeiras 50 observações.
    """
    features = [
        "categoria",
        "preco_incl_tax",
        "disponibilidade_produto",
        "qtde_estrelas",
    ]

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Dados não disponíveis.")

    df_features = df_livros[features].copy()

    dataType = df_features.dtypes.apply(lambda x: str(x)).to_dict()
    infoEstat = df_features.describe().to_dict()
    features = df_features.head(50).to_dict(orient="records")

    return {"dataType": dataType, "infoEstat": infoEstat, "features": features}


@app.get("/api/v1/ml/training-data", tags=["ML-Ready"])
def ml_training_data():
    """
    Endpoint para retornar os dados de treinamento para um modelo de Machine Learning.
    Foi adotada a divisão de treino e teste, com 70% das observações para treino e 30% para teste.
    Para garantir a reprodutibilidade, foi fixado o random_state em 42.
    """

    var_independente = ["preco_incl_tax", "disponibilidade_produto", "qtde_estrelas"]

    var_dependente = "categoria"

    colunas_necessarias = var_independente + [var_dependente]

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Dados não disponíveis.")

    df_ml = df_livros[colunas_necessarias]

    # Divisão entre variáveis independentes e dependentes
    X = df_ml[var_independente]
    y = df_ml[var_dependente]

    # Divisão em conjunto de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Concatenando os conjuntos de treino e teste
    train = concat([X_train, y_train.reset_index(drop=True)], axis=1).dropna()
    test = concat([X_test, y_test.reset_index(drop=True)], axis=1).dropna()

    return {
        "train": train.to_dict(orient="records"),
        "test": test.to_dict(orient="records"),
    }


@app.post("/api/v1/ml/predictions", tags=["ML-Ready"])
def fazer_predicao(payload: EntradaModelo):
    """
    Os valores previstos nesse endpoint são de caráter informativo e mostram o potencial da API para incorporar modelos de ML.
    \nA acurácia do modelo utilizado é de apenas 16%, por isso não deve ser utilizada para tomada de decisões.
    """
    try:
        df = DataFrame([item.dict() for item in payload.itens])
        resultado = prever_categoria(df)
        return resultado.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
