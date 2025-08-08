import requests
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pandas import DataFrame
from tqdm import tqdm

url = "https://books.toscrape.com/"  # URL em que será aplicada a raspagem


def retorna_inteiro(texto):
    regex = re.search(r"\((\d+) available\)", texto)
    if regex:
        return int(regex.group(1))
    return 0


def path_completo(nome_arquivo_csv):
    pasta_atual = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta_atual = os.path.join(pasta_atual, "data")
    os.makedirs(pasta_atual, exist_ok=True)
    caminho_completo_csv = os.path.join(pasta_atual, nome_arquivo_csv)
    return caminho_completo_csv


def response_soup(url):
    """Recebe uma URL e retorna o objeto BeautifulSoup."""

    try:
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    except requests.exceptions.RequestException as erro:
        print(f"Erro ao acessar a página: {erro}")
        return None


def lista_categorias(soup, url):
    """Função que recebe uma URL e retorna uma lista de categorias de livros"""

    lista_cats = []
    try:
        ul_principal = soup.find("ul", class_="nav nav-list")
        ul_sub = ul_principal.find_next("ul")

        for categoria in tqdm(
            ul_sub.find_all("li"), desc="Extraindo categorias", ncols=100
        ):
            no_categoria = categoria.get_text(strip=True)
            link_categoria = urljoin(
                url, categoria.find("a")["href"]
            )  # Obtém o link da categoria

            lista_cats.append((no_categoria, link_categoria))

    except AttributeError as erro:
        print(f"Erro ao encontrar categorias: {erro}")

    return lista_cats


def listar_titulos(categorias, url):
    """Função que recebe a lista de categorias e retorna com os titulos dos livro de cada categoria"""

    lista_titulos = []
    for categoria in tqdm(
        categorias, desc="Extraindo a relação de titulos por categoria", ncols=100
    ):
        cat = categoria[0]
        link_categoria = categoria[1]
        url_atual = link_categoria

        while True:
            soup = response_soup(url_atual)
            if not soup:
                break

            livros = soup.find_all("article", class_="product_pod")
            for livro in livros:
                titulo = livro.h3.a["title"]
                href_livro = livro.find("a")["href"]
                link_livro = urljoin(link_categoria, href_livro)
                lista_titulos.append((cat, url_atual, titulo, link_livro))

            # Verifica se há uma próxima página
            proxima_pagina = soup.find("li", class_="next")
            if proxima_pagina:
                proximo_link = proxima_pagina.a["href"]
                url_atual = urljoin(url_atual, proximo_link)
            else:
                break

    return lista_titulos


def detalhes_livro(lista_titulos, url):
    """Função que recebe a lista de livros e retorna os detalhes de cada um."""

    detalhes = []

    estrelas_dicionario = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    for titulos in tqdm(lista_titulos, desc="Extraindo detalhes dos livros", ncols=100):
        categoria, url_categoria, titulo, link_livro = titulos
        soup = response_soup(link_livro)
        if not soup:
            continue

        # Captura a url da imagem do livro
        url_imagem = soup.find("img")["src"]
        url_imagem_completa = urljoin(url, url_imagem)

        # Obtém os detalhes do livro
        descricao_div_ant = soup.find("div", id="product_description")
        if descricao_div_ant:
            p_descricao = descricao_div_ant.find_next("p")
            descricao_produto = p_descricao.get_text(strip=True)
        else:
            descricao_produto = "Descrição não disponível"

        # Captura a qauantidade de estrelas
        estrelas_objeto = soup.find("p", class_="star-rating").get("class")[1]
        qtde_estrelas = estrelas_dicionario.get(estrelas_objeto, 0)

        # Retorna informações do produto

        # Inicializa as variáveis
        var_upc = ""
        tipo_produto = ""
        preco_excl_tax = ""
        preco_incl_tax = ""
        imposto = ""
        disponibilidade_produto = 0
        numero_reviews = 0

        tabela_detalhes = soup.find("table", class_="table table-striped")
        if tabela_detalhes:
            for linha in tabela_detalhes.find_all("tr"):
                cabecalho = linha.find("th").get_text(strip=True)
                valor = linha.find("td").get_text(strip=True)
                if cabecalho == "UPC":
                    var_upc = valor
                elif cabecalho == "Product Type":
                    tipo_produto = valor
                elif cabecalho == "Price (excl. tax)":
                    preco_excl_tax = valor.replace("£", "").strip()
                elif cabecalho == "Price (incl. tax)":
                    preco_incl_tax = valor.replace("£", "").strip()
                elif cabecalho == "Tax":
                    imposto = valor.replace("£", "").strip()
                elif cabecalho == "Availability":
                    disponibilidade_produto = retorna_inteiro(valor)
                elif cabecalho == "Number of reviews":
                    numero_reviews = valor

        detalhes.append(
            {
                "categoria": categoria,
                "url_categoria": url_categoria,
                "titulo": titulo,
                "link_livro": link_livro,
                "url_imagem": url_imagem_completa,
                "descricao_produto": descricao_produto,
                "qtde_estrelas": qtde_estrelas,
                "upc": var_upc,
                "tipo_produto": tipo_produto,
                "moeda": "£",
                "preco_excl_tax": preco_excl_tax,
                "preco_incl_tax": preco_incl_tax,
                "imposto": imposto,
                "disponibilidade_produto": disponibilidade_produto,
                "numero_de_reviews": numero_reviews,
            }
        )

    return detalhes


def main():
    """Função principal para raspar o site Books to Scrape"""

    print("\nIniciando a raspagem dos livros ...")

    soup = response_soup(url)
    categorias = lista_categorias(soup, url)
    titulos = listar_titulos(categorias, url)
    detalhes = detalhes_livro(titulos, url)
    path_salvar = path_completo("books_dataset.csv")

    df_books = DataFrame(detalhes)
    df_books.index.name = "id"
    df_books.to_csv(path_salvar, encoding="utf-8", sep=";")

    print(f"\nRaspagem finalizada!!!")


if __name__ == "__main__":
    main()
