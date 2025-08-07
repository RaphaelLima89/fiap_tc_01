# Plano Arquitetural

## 1. Pipeline de Dados

```text
[ Web Scraping ]
        ↓
[ Dataset CSV Local (data/books_dataset.csv) ]
        ↓
[ API RESTful (FastAPI) ]
        ↓
[ Consumo externo via aplicação, cientista de dados ou modelos de Machine Learning ]   
```

- **Ingestão**: Utiliza as bibliotecas `BeautifulSoup e requests` para raspar as informações do site [books.toscrape.com](https://books.toscrape.com).
- **Processamento**: Após a captura, os dados são organizados em um formato flat e salvos em um arquivo `.csv`.
- **Serviço de API**: A API desenvolvida em FastAPI carrega o arquivo `.csv` e disponibiliza o conteúdo por meio de `endpoints`.
- **Consumo**: Usuários ou serviços podem consumir os dados pela API, no caso de uso para modelos de ML, a API dispõe de endpoints dedicados para esse escopo.

---

## 2. Arquitetura escalável

A arquitetura está organizada em módulos, facilitando a manutenção e a inclusão de recursos futuros:

- **Organização dos módulos**:
    - `api/`        concentra os arquivos necessários para a aplicação.
    - `data/`       armazena a base dados extraída por meio de scrape.
    - `logs/`       armazena os logs estruturados de todas as chamadas.
    - `models/`     armazena os artefatos de ML utilizados neste projeto.
    - `scripts/`    reúne o scripts que foram utilizados para o scrape e modelo teste para aplicação de ML 

- **Armazenamento**    
    - O projeto atualmente utiliza um arquivo `.csv` como fonte de dados, mas é possível migrar para um banco de dados relacional ou mesmo um
    NoSQL, caso seja necessário.
---

## 3. Cenário de uso para cientistas de dados/ML

O projeto contempla endpoints dedicados para cientistas de dados e o uso em ML:

- O endpoint `/api/v1/ml/features` foi desenvolvido para fornecer conjuntos de metadados das variáveis mais relevantes, incluindo os tipos de dados, um breve resumo estatístico das variáveis, além, é claro, das features.
- Na hipótese de se desejar treinar novos modelos, o endpoint `/api/v1/ml/training-data` fornece os dados na divisão de treino e teste, com 70% das observações para treino e 30% para teste. 

---

## 4. Plano de integração com modelos de ML

- Na versão em que se encontra o projeto, foi disponibilizado um modelo de classificação treinado e salvo na pasta `models`.
- O endpoint `/api/v1/ml/predictions` permite utilizar o modelo mencionado anteriormente, enviando as variáveis independentes e recebendo a categoria prevista.
- A arquiteura desenhada permite a substituição do modelo facilmente e sem interromper o serviço dos demais enpoints.
---
