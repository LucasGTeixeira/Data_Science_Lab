# Data_Science_Lab

Portfólio de estudos avançados em Machine Learning, Estatística e Engenharia de ML.
Monorepo com projetos profundos (não tutoriais), cada um demonstrando rigor
estatístico, visão de negócio e código de produção.

## Filosofia: Docker-first

Nada é instalado via `venv` no host. O laboratório roda em um container com
JupyterLab + Apache Spark, e a pasta `Laboratoy/` é montada como volume — os
notebooks ficam no host e são executados no container.

```
.
├── Dockerfile              # FROM jupyter/pyspark-notebook + requirements
├── requirements.txt        # deps extras do laboratório
├── docker-compose.yml      # serviço jupyter-spark
└── Laboratoy/
    └── <experimento>/
        ├── notebooks/      # EDA, experimentos e relatórios
        ├── data/           # datasets (não versionados)
        ├── engineering/    # código modular, jobs, features
        └── docs/           # decisões, métricas, relatórios
```

## Pré-requisitos

- Docker Engine + Compose v2 (`docker compose version`).

## Como usar

O serviço `lab` (sem profile) sobe com o comando padrão e enxerga todo o
`Laboratoy/`. Serviços de projeto ficam atrás de um profile, para isolar
dependências pesadas.

Tudo (laboratório completo):

```bash
docker compose up --build
```

Só um projeto, container isolado:

```bash
docker compose up --build warframe-market-analysis
```

Abra http://localhost:8888 (lab) ou http://localhost:8889 (warframe) e use o
token que aparece no log. A pasta `Laboratoy/` aparece em `/home/jovyan/work`;
no serviço `warframe-market-analysis` o projeto também fica em
`/home/jovyan/work/warframe`.

O Spark roda em modo local — crie a sessão com `.master("local[*]")`:

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").appName("lab").getOrCreate()
```

Derrubar: `docker compose down`.

## Adicionar um experimento

1. Copie um serviço existente no `docker-compose.yml` (o bloco `warframe-market-analysis`).
2. Dê um nome novo, escolha uma `profile` e uma porta livre (evite colisão com `:8888`/`:8889`).
3. Aponte o volume para a pasta do projeto e nomeie o caminho interno (o "alias").
4. `docker compose up --build <nome>` sobe só ele; `docker compose up` sobe o `lab`.

## Dependências extras

A imagem base já traz `pyspark`, `pandas`, `numpy`, `matplotlib` e
`scikit-learn`. Para adicionar mais, edite `requirements.txt` e rode
`docker compose up --build`.

## Projetos

| # | Projeto | Foco técnico | Status |
|---|---------|--------------|--------|
| 01 | [Warframe Market Analysis](Laboratoy/01-warframe-market-analysis) | Spark, engenharia de features, séries temporais de preços | scaffold |

Cada projeto deve ter seu próprio `README.md` cobrindo: problema de negócio,
arquitetura e metodologia, principais resultados e instruções reproduzíveis.
