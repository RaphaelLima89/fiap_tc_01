from fastapi import FastAPI
from fastapi import HTTPException
from pandas import read_csv
from pandas import DataFrame
import os
from typing import Optional


app = FastAPI(
    title="API Pública para Consulta de Livros",
    version="1.0.0",
    description="API para consulta de livros do site Book to Scrape, categorias e detalhes de livros.",
)

def carregar_dataframe():
    """
    Função que carrega o DataFrame de livros a partir de um arquivo CSV.
    """
    path_csv = os.path.join(os.path.dirname(__file__),  "books_dataset.csv").replace("\\api\\", "\\data\\")
    if not os.path.exists(path_csv):
        print("Arquivo CSV não encontrada. Tente rodar novamente o script de raspagem.")
        return DataFrame()
    df_livros = read_csv(path_csv, encoding="utf-8", header=0, sep=";")
    return df_livros
    

# Endpoints Core

@app.get("/api/v1/books")
def listar_livros():
    """
    Endpoint para listar todos os livros disponíveis.
    """
    df_livros = carregar_dataframe()
    if df_livros.empty:
        return {"message": "Nenhum livro encontrado."}
    return df_livros.to_dict(orient="records")


@app.get("/api/v1/books/search")
def buscar_livros(titulo: Optional[str] = None, categoria: Optional[str] = None):

    """
    Endpoint para buscar livros por título e/ou categoria.
    """

    df_livros = carregar_dataframe()

    selecao = df_livros.copy()

    if titulo is not None and titulo != "":
        selecao = selecao[selecao["titulo"].str.contains(titulo, case=False, na=False)]
    if categoria is not None and categoria != "":
        selecao = selecao[selecao["categoria"].str.contains(categoria, case=False, na=False)] 
                        
    if selecao.empty:
        raise HTTPException(status_code=404, detail="Busca não retornou nenhum livro.")
    
    return selecao.to_dict(orient="records")


@app.get("/api/v1/books/{id_livro}")
def retorna_livro_por_id(id_livro: int):
    """
    Endpoint para retornar livro específico pelo ID.
    """

    df_livros = carregar_dataframe()
    livro_selecionado = df_livros[df_livros["id"] == id_livro]
    if livro_selecionado.empty:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    return livro_selecionado.to_dict(orient="records")[0]

@app.get("/api/v1/categories")
def listar_categorias():
    """
    Endpoint para listar as categorias que estão disponíveis no dataset.
    """

    df_livros = carregar_dataframe()
    lista_categorias = df_livros["categoria"].unique().tolist()
    if not lista_categorias:
        raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada.")
    return {"categorias": lista_categorias}


@app.get("/api/v1/health")
def health_check():
    """
    Endpoint para verificar a saúde da API.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=500, detail="API online, mas o dataset não pôde ser carregados corretamente.")

    return {"status": "API online e dataset carregado."}

# Endpoints de Insights

@app.get("/api/v1/stats/overview")
def stats_overview():

    """
    Endpoint para obter uma visão geral dos dados.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Estatísticas não disponíveis.")

    total_livros = len(df_livros)
    preco_medio = df_livros["preco_incl_tax"].mean()
    distribuicao_rating = df_livros["qtde_estrelas"].value_counts().sort_index().to_dict()

    return {
        "total_livros": total_livros,
        "preco_medio": preco_medio,
        "distribuicao_rating": distribuicao_rating
    }

    
@app.get("/api/v1/stats/categories")
def stats_categories():

    """
    Endpoint com as estatísitcas por categoria.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Estatísticas por categoria não disponíveis.")
    
    stats_categories = df_livros.groupby("categoria").agg(
        total_livros=("id", "count"),
        preco_medio=("preco_incl_tax", "mean"),
        rating_medio=("qtde_estrelas", "mean")
    )

    stats_categories = stats_categories.reset_index().to_dict(orient="records")
    return {"stats_categories": stats_categories}

@app.get("/api/v1/books/top-rated")
def top_rated_books(top: Optional[int] =50):
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


@app.get("/api/v1/stats/price-range")
def stats_price_range(min: float, max: float):

    """
    Endpoint para obter os livros dentro de um intervalo de preço.
    """

    df_livros = carregar_dataframe()
    if df_livros.empty:
        raise HTTPException(status_code=404, detail="Dados não disponíveis.")

    selecao = df_livros[(df_livros["preco_incl_tax"] >= min) & (df_livros["preco_incl_tax"] <= max)]

    colunas_filtradas = ["id", "categoria", "titulo", "categoria", "preco_incl_tax", "qtde_estrelas"]
    selecao = selecao[colunas_filtradas]

    if selecao.empty:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado nesse intervalo de preço.")

    return selecao.to_dict(orient="records")