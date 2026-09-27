# Data_Science_Lab

Portfólio de estudos avançados em Machine Learning, Estatística e Engenharia de ML.
Monorepo com 3-4 projetos profundos (não tutoriais), cada um demonstrando rigor
estatístico, visão de negócio e código de produção.

## Projetos

| # | Projeto | Foco técnico | Dataset sugerido |
|---|---------|--------------|------------------|
| 01 | [Causal Inference Marketing](01-causal-inference-marketing) | PSM, Diff-in-Diff, Synthetic Control, Uplift/HTE | Starbucks Offer, LendingClub, ANP |
| 02 | [Credit Risk XAI](02-credit-risk-xai) | LightGBM/XGBoost vs GAM, SHAP/LIME, calibração, PSI | Home Credit, IEEE-CIS Fraud |
| 03 | [Hierarchical Demand Forecasting](03-hierarchical-demand-forecasting) | Previsão probabilística, reconciliação hierárquica, CRPS | M5 Walmart, PJM Energy |
| 04 | [Fraud Detection MLOps](04-fraud-detection-mlops) | FastAPI, Docker, MLflow, drift monitoring, CI/CD | NYC Taxi, Spotify Skip |

## Estrutura padrão de cada projeto

```
<projeto>/
├── data/        # datasets (não versionados, veja .gitignore)
├── notebooks/   # EDA, experimentos e relatórios
├── src/         # código modular e reutilizável
└── tests/       # testes unitários (pytest)
```

Cada projeto deve ter seu próprio `README.md` cobrindo: problema de negócio,
arquitetura e metodologia, principais resultados e instruções reproduzíveis.

## Como usar

1. Entre na pasta do projeto escolhido.
2. Crie e ative um ambiente (`poetry install` ou `uv venv && uv pip install -r requirements.txt`).
3. Coloque os dados em `data/` e comece pelos notebooks.

> Guias locais de Git e Docker ficam em `guides/` (não versionados).
