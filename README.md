
# API Pública para Consulta de Livros do site Books to Scrape - Tech Challenge FIAP 1

Este projeto tem como objetivo implementar uma **API RESTful pública** para consulta em uma base de dados extraída do site [Books to Scrape](https://books.toscrape.com/). O projeto contempla uma rotina de web scraping, uma API RESTful, além de um exemplo de modelo de machine learning.

---

## Funcionalidades da API

- Listagem de todos os livros disponíveis na base de dados
- Consultas por ID da base, por título, por categoria, faixa de preço, ou ainda listar todas as categorias disponíveis
- Listagem dos livros com as melhores avaliações
- Estatísticas gerais, como o total de livro, preço médio, distribuição de ratings
- Estatísticas detalhadas por categoria, com a quantidade de livros e o preço por categoria
- Autenticação com JWT para rotas sensíveis
- Endpoint com aplicação de um modelo de Machine Learning

---

## Tecnologias utilizadas

O projeto foi todo desenvolvido em a linguagem **Python 3.13.4** e as principais bibliotecas foram:

- **FastAPI** - biblioteca principal da API
- **Prometheus FastAPI Instrumentator** - Métricas e performance da API
- **JWT** - Autenticação com FastAPI
- **BeautifulSoup + Requests** - para o Web scraping
- **Pandas** - para manipulação de dados
- **Scikit-Learn** - biblioteca mais difundida na comunidade para modelos de Machine Learning
- **Joblib** - Realizar a dump dos modelos

---

## 📁 Estrutura do Projeto
```bash
├── api/
│   ├── app.py                  # Arquivo principal da API
│   ├── auth.py                 # Autenticação JWT
│   ├── log_config.py           # Logger estruturado
│   └── modelo_utils.py         # Funções e classes do modelo ML
├── scripts/
│   └── web_scraping_books.py   # Script de web scraping
├── data/
│   └── books_dataset.csv       # Dataset gerado pelo scraping
├── models/
│   ├── modelo_bookscrape.pkl   # Modelo treinado
│   └── encoder.pkl             # Encoder de categorias
├── logs/
│   └── api.log                 # Log de requisições
├── requirements.txt            # Dependências do projeto
└── README.md                   # Arquivo contendo principais informações do projeto
```

---

## Instruções de instalação e configuração

### 1. Clone o repositório

```bash
git clone https://github.com/RaphaelLima89/fiap_tc_01
cd fiap_tc_01
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Instalando bibliotecas necessárias

```bash
pip install -r requirements.txt
```

### 4. Executando o script do Web Scraping

```bash
python scripts/web_scraping_books.py
```

### 5. Logs da API
Para evitar **sujeiras** de rastreabilidade, recomenda-se a limpeza do arquivo api.log antes de iniciar o uso da API, ou eventualmente seu deploy.

### 6. Iniciando a API
Navegue até a pasta Projeto e então execute o seguinte comando

```bash
cd projeto
uvicorn projeto.api.app:app --reload
```
Acesse o endereço [http://localhost:8000/docs](http://localhost:8000/docs) para utilizar a documentação via Swagger.

---

## Documentação das rotas da API

| Método    | Endpoint |                Descrição                       |
|-----------|----------|--------------------------------------------    |
| `GET`     | `/api/v1/books`                                           | Lista todos os livros disponíveis na base de dados            |
| `GET`     | `/api/v1/books/{id}`                                      | Retorna detalhes completos de um livro específico pelo **id** |
| `GET`     | `/api/v1/books/search?title={title}&category={category}`  | Busca livros por **título** e/ou **categoria**                |
| `GET`     | `/api/v1/categories`                                      | Lista todas as categorias de livros disponíveis               |
| `GET`     | `/api/v1/health`                                          | Verifica status da API e conectividade com os dados           |
| `GET`     | `/api/v1/stats/overview`                                  | Estatísticas gerais da coleção                                |
| `GET`     | `/api/v1/stats/categories`                                | Estatísticas detalhadas por categoria                         |
| `GET`     | `/api/v1/books/top-rated`                                 | Lista os livros com melhor avaliação (rating mais alto)       |
| `GET`     | `/api/v1/books/price-range?min={min}&max={max}`           | Filtra livros dentro de uma faixa de preço específica         |
| `POST`    | `/api/v1/auth/login`                                      | Obtém token em JWT para rotas sensíveis                       |
| `GET`     | `/api/v1/scraping/trigger`                                | Aciona scraping (requer token)                                |
| `GET`     | `/api/v1/ml/features`                                     | Dados formatados para features, orientado para modelos de ML  |
| `GET`     | `/api/v1/ml/training-data`                                | Dataset para treinamento                                      |
| `POST`    | `/api/v1/ml/predictions`                                  | Endpoint para receber predições                               |

---

## Exemplos de chamadas com requests/responses

### Exemplo 1 - Captura detalhes de um livros pelo id

GET `/api/v1/books/{id}`

**Chamada na rota:**

```bash
curl -X GET http://localhost:8000/api/v1/books/99
```

**Resposta:**

```json
{
    "id":12,
    "categoria":"Mystery",
    "url_categoria":"https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "titulo":"In a Dark, Dark Wood",
    "link_livro":"https://books.toscrape.com/catalogue/in-a-dark-dark-wood_963/index.html",
    "url_imagem":"https://books.toscrape.com/media/cache/95/84/95840dfd67c020067c99d70451147e20.jpg",
    "descricao_produto":"In a dark, dark wood Nora hasn't seen Clare for ten years. Not since Nora walked out of school one day and never went back. There was a dark, dark houseUntil, out of the blue, an invitation to Clare’s hen do arrives. Is this a chance for Nora to finally put her past behind her?And in the dark, dark house there was a dark, dark roomBut something goes wrong. Very wrong.And i In a dark, dark wood Nora hasn't seen Clare for ten years. Not since Nora walked out of school one day and never went back. There was a dark, dark houseUntil, out of the blue, an invitation to Clare’s hen do arrives. Is this a chance for Nora to finally put her past behind her?And in the dark, dark house there was a dark, dark roomBut something goes wrong. Very wrong.And in the dark, dark room.... Some things can’t stay secret for ever. ...more",
    "qtde_estrelas":1,
    "upc":"19ed25f4641d5efd",
    "tipo_produto":"Books",
    "moeda":"£",
    "preco_excl_tax":19.63,
    "preco_incl_tax":19.63,
    "imposto":0.0,
    "disponibilidade_produto":18,
    "numero_de_reviews":0    
}
```

---

### Exemplo 2 - Lista todas as categorias de livros disponíveis

GET `/api/v1/categories`

**Chamada na rota:**

```bash
curl -X GET http://localhost:8000/api/v1/categories
```

**Resposta:**

```json
{
    "categorias": [
    "Travel",
    "Mystery",
    "Historical Fiction",
    "Sequential Art",
    "Classics",
    "Philosophy",
    "Romance",
    "Womens Fiction",
    "Fiction",
    "Childrens",
    "Religion",
    "Nonfiction",
    "Music",
    "Default",
    "Science Fiction",
    "Sports and Games",
    "Add a comment",
    "Fantasy",
    "New Adult",
    "Young Adult",
    "Science",
    "Poetry",
    "Paranormal",
    "Art",
    "Psychology",
    "Autobiography",
    "Parenting",
    "Adult Fiction",
    "Humor",
    "Horror",
    "History",
    "Food and Drink",
    "Christian Fiction",
    "Business",
    "Biography",
    "Thriller",
    "Contemporary",
    "Spirituality",
    "Academic",
    "Self Help",
    "Historical",
    "Christian",
    "Suspense",
    "Short Stories",
    "Novels",
    "Health",
    "Politics",
    "Cultural",
    "Erotica",
    "Crime"
  ]
}
```

---

## Autor

**Raphael F Lima**
Aluno FIAP | Pos Tech - Machine Learning Engineering