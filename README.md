
# API Pública para Consulta de Livros do site Books to Scrape - Tech Challenge FIAP 1

Este projeto tem como objetivo implementar uma **API RESTful pública** para consulta em uma base de dados extraída do site [Books to Scrape](https://books.toscrape.com/). O projeto contempla uma rotina de web scraping, uma API RESTful, além de um exemplo de modelo de machine learning.

---

## Funcionalidades da API

- Listagem de todos os livros disponíves na base de dados
- Consultas por ID da base, por título, por categoria, faixa de preço, ou ainda listar todas as categorias disponíveis
- Listagem dos livros com as melhores avaliações
- Estatísticas gerais, como o total de livro, preço médio, distribuição de ratings
- Estatísticas detalheas por categoria, com a quntidade de livros e o preço por categoria
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
git clone 

