# Analisador de Partidas de CS2

[![Testes automatizados](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml/badge.svg)](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml)

Projeto de estudo em **Python e SQLite**, com **Pytest** e GitHub Actions, para
registrar partidas de CS2 e o desempenho dos jogadores. O foco é praticar SQL,
qualidade de dados e testes automatizados.

O registro de partidas e performances, a consulta do histórico e as métricas de
desempenho estão implementados. Análises por mapa e interface gráfica são etapas
futuras. O banco armazena somente dados brutos nas tabelas `player`, `partida` e
`performance`; as métricas são calculadas nas consultas.


O projeto permite registrar partidas, armazenar performances individuais
e consultar o histórico de partidas de um jogador, com ordenação
cronológica e validação de integridade no banco de dados.

As métricas K/D, KDA, HS%, ADR e KAST% estão implementadas por partida e no
resumo acumulado do jogador, que também inclui Win Rate. As análises por
mapa e uma interface gráfica permanecem como funcionalidades futuras.

## Quality Assurance

O projeto possui **138 testes automatizados com Pytest aprovados localmente**
(116 anteriores preservados e 22 novos testes de métricas), além de **4 cenários
de integração documentados com evidências**. A validação desta atualização no
**GitHub Actions ainda não foi realizada**.

| ID | Cenário de integração | Resultado |
|---|---|---|
| **QA-INT-001** | Rejeição de performance inválida e rollback | **PASSOU** |
| **QA-INT-002** | Registro válido e verificação com SQL JOIN | **PASSOU** |
| **QA-INT-003** | Consulta de histórico, ordenação e isolamento entre jogadores | **PASSOU** |
| **QA-INT-004** | Validação das métricas de desempenho | **PASSOU** |

Os cenários verificam integridade de dados, transações, consultas SQL e métricas
de desempenho.
Foram executados por scripts Python iniciados manualmente, com
verificações por `assert`.

**[Consultar documentação completa, resultados e evidências](QA.md)**

## Instalação e testes

Na pasta do repositório, com Python 3.12:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

Os 138 testes verificam regras do schema, registros válidos e inválidos,
relacionamentos, duplicatas, persistência, rollback, consultas do histórico
de partidas e cálculos individuais e acumulados de métricas.

## Utilização

```python
from src.db import connect, init_db
from src.registros import registrar_partida, registrar_performance

conn = connect("cs2.sqlite")
try:
    init_db(conn)
    with conn:
        # Exemplo de cadastro do jogador; não há função Python para isso ainda.
        player_id = conn.execute(
            "INSERT INTO player (nickname) VALUES (?)", ("jogador_exemplo",)
        ).lastrowid
        partida_id = registrar_partida(
            conn, "2026-10-20", "de_mirage", "vitoria", 13, 7
        )
        performance_id = registrar_performance(
            conn,
            player_id=player_id, partida_id=partida_id,
            kills=20, deaths=12, assists=4, headshots=9, damage=2100,
            utility_damage=80, enemies_blinded=7, flash_assists=2,
            rounds_played=20, first_kills=3, first_deaths=2, kast_rounds=15,
        )
finally:
    conn.close()
```

O exemplo pressupõe um nickname ainda não cadastrado. Para um jogador existente,
use seu `player_id` em vez de repetir o cadastro.

As funções recebem uma conexão existente, usam SQL parametrizado e retornam o
ID inserido. Elas não fazem `commit`: no exemplo, `with conn` confirma a transação
se houver sucesso ou a desfaz se ocorrer uma exceção. O fechamento é explícito.

O schema valida os dados com constraints e triggers, incluindo resultado
coerente com o placar e `rounds_played` igual à soma dos rounds. Violações são
propagadas como `sqlite3.IntegrityError`.

## Estrutura

```text
sql/schema.sql               # Tabelas e regras de integridade
src/db.py                    # Conexão e inicialização
src/registros.py             # Registro de partidas e performances
tests/test_schema.py         # Regras do banco
tests/test_partidas.py       # Registro de partidas
tests/test_performances.py   # Registro de performances
src/consultas.py             # Consulta do histórico de partidas
tests/test_consultas.py      # Testes da consulta do histórico
src/metricas.py              # Métricas por partida e resumo do jogador
tests/test_metricas.py       # Testes das métricas de desempenho
```

Decisões e planejamento estão em [NOTAS.md](NOTAS.md).
