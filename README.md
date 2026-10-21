# Analisador de Partidas de CS2
[![Testes automatizados](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml/badge.svg)](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml)

Sistema pequeno em **Python + SQL (SQLite)** para registrar partidas de CS2, guardar dados brutos de desempenho e calcular métricas depois. Projeto de estudo com foco em **qualidade de dados** e **fundamentos de QA**.

## Tecnologias utilizadas

- **Python:** desenvolvimento da aplicação e processamento de dados.
- **SQLite:** armazenamento dos dados das partidas.
- **SQL:** modelagem, consultas e validação de dados.
- **Pytest:** testes automatizados e validação das regras de negócio.

## Status
MVP 1 em andamento: modelagem e schema concluídos, com testes das regras de qualidade.
Registro de partidas implementado em `src/partidas.py` e de performances em
`src/performances.py`; consultas e métricas continuam pendentes.

## Registrar uma partida

```python
from src.db import connect, init_db
from src.partidas import registrar_partida

conn = connect("cs2.sqlite")
try:
    init_db(conn)
    with conn:
        partida_id = registrar_partida(
            conn, "2026-10-20", "de_mirage", "vitoria", 13, 7
        )
    print(partida_id)
finally:
    conn.close()
```

Os cinco valores correspondem, na ordem, às colunas `data_partida`, `mapa`,
`resultado`, `rounds_time` e `rounds_adversario`. O ID retornado é gerado pelo
SQLite. A função usa SQL parametrizado e deixa a validação para o schema;
violações de integridade geram `sqlite3.IntegrityError`.

A função não faz `commit` nem fecha a conexão. No exemplo, `with conn` confirma
a transação ao terminar com sucesso ou desfaz as alterações se ocorrer uma
exceção. Também é possível usar `conn.commit()` e `conn.rollback()` explicitamente.
Receber um ID não significa que a transação já foi confirmada.

## Registrar uma performance

Use uma conexão criada por `connect()` e IDs de jogador e partida existentes.
Para uma partida de 13×7, `rounds_played` deve ser 20:

```python
from src.performances import registrar_performance

# conn já aberta; player_id e partida_id identificam registros existentes.
with conn:
    performance_id = registrar_performance(
        conn,
        player_id=player_id, partida_id=partida_id,
        kills=20, deaths=12, assists=4, headshots=9, damage=2100,
        utility_damage=80, enemies_blinded=7, flash_assists=2,
        rounds_played=20, first_kills=3, first_deaths=2, kast_rounds=15,
    )
```

Depois de `conn`, os parâmetros são obrigatoriamente passados por nome. Cada
nome corresponde diretamente à coluna SQL, incluindo `kast_rounds` (contagem
bruta, sem calcular KAST%). A função retorna o ID gerado e não confirma a
transação. Chaves estrangeiras validam os IDs, `UNIQUE` impede repetir o mesmo
par jogador/partida, `CHECK` valida os valores e a trigger confere os rounds
com o placar. Violações continuam gerando `sqlite3.IntegrityError`.

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
│   ├── db.py
│   ├── partidas.py
│   └── performances.py
├── tests/
│   ├── test_schema.py
│   ├── test_partidas.py
│   └── test_performances.py
├── NOTAS.md
├── README.md
└── requirements.txt
```
