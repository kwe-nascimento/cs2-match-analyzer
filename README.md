# Analisador de Partidas de CS2

Sistema pequeno em **Python + SQL (SQLite)** para registrar partidas de CS2, guardar dados brutos de desempenho e calcular métricas depois. Projeto de estudo com foco em **qualidade de dados** e **fundamentos de QA**.

## Status
MVP 1 em andamento: modelagem e schema concluídos, com testes das regras de qualidade.

## Modelo de dados
- `player`: o jogador
- `partida`: data, mapa, resultado e placar
- `performance`: o que o jogador fez em uma partida (dados brutos)

Princípio: o banco guarda **somente dados brutos**. K/D, KDA, HS%, ADR, KAST% e Win Rate são calculados depois.

## Regras de qualidade
Validadas no banco (`CHECK` e triggers) e cobertas por testes em `tests/test_schema.py`: valores não negativos, `headshots <= kills`, `kast_rounds <= rounds_played`, rounds batendo com o placar, resultado coerente com o placar, data em AAAA-MM-DD, sem performance duplicada.

## Como rodar os testes
```bash
pip install -r requirements.txt
pytest
```

## Estrutura
```
cs2-match-analyzer/
├── sql/
│   └── schema.sql
├── src/
│   └── db.py
├── tests/
│   └── test_schema.py
├── NOTAS.md
├── README.md
└── requirements.txt
```
