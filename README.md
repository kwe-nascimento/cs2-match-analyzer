# Analisador de Partidas de CS2

[![Testes automatizados](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml/badge.svg)](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml)

Projeto de estudo em **Python e SQLite**, com **Pytest** e GitHub Actions, para
registrar partidas de CS2 e o desempenho dos jogadores. O foco é praticar SQL,
qualidade de dados e testes automatizados.

O registro de partidas e performances, a consulta do histórico e as métricas de
desempenho e as análises por mapa estão implementados. A interface gráfica é uma
etapa futura. O banco armazena somente dados brutos nas tabelas `player`, `partida` e
`performance`; as métricas são calculadas nas consultas.


O projeto permite registrar partidas, armazenar performances individuais
e consultar o histórico de partidas de um jogador, com ordenação
cronológica e validação de integridade no banco de dados.

As métricas K/D, KDA, HS%, ADR e KAST% estão implementadas por partida e no
resumo acumulado do jogador, que também inclui Win Rate. As análises por
mapa incluem Best/Worst Map; a interface gráfica permanece como funcionalidade futura.

## Quality Assurance

O projeto possui **195 testes automatizados com Pytest aprovados localmente**
(167 anteriores preservados e 28 novos testes de análise por mapa), além de **5 cenários
manuais de integração documentados e aprovados, com evidências**. O commit `289c378` também teve os 138 testes aprovados no GitHub Actions: [execução confirmada de 28/10/2026](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40775358994).

| ID | Cenário de integração | Resultado |
|---|---|---|
| **QA-INT-001** | Rejeição de performance inválida e rollback | **PASSOU** |
| **QA-INT-002** | Registro válido e verificação com SQL JOIN | **PASSOU** |
| **QA-INT-003** | Consulta de histórico, ordenação e isolamento entre jogadores | **PASSOU** |
| **QA-INT-004** | Validação das métricas de desempenho | **PASSOU** |
| **QA-INT-005** | Análise de desempenho por mapa e Best/Worst Map | **PASSOU** |

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

Os 195 testes verificam regras do schema, registros válidos e inválidos,
relacionamentos, duplicatas, persistência, rollback, consultas do histórico
de partidas, cálculos individuais e acumulados de métricas, validade das datas
e consistência dos placares após atualização, agregação por mapa e classificação
Best/Worst Map.

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
src/mapas.py                # Estatísticas por mapa e Best/Worst Map
tests/test_mapas.py          # Testes das análises por mapa
```

Decisões e planejamento estão em [NOTAS.md](NOTAS.md).

## Cobertura de testes

```bash
python -B -m pytest -q -p no:cacheprovider --cov=src --cov-branch --cov-report=term-missing
```

O relatório mostra linhas, branches e linhas não cobertas, sem percentual mínimo
obrigatório. Para HTML, use `--cov-report=html`; a saída `htmlcov/` é ignorada
pelo Git. O workflow exibirá cobertura nos logs após a publicação.
A base `0c17c96` teve 167 testes e 100% de cobertura Python aprovados no GitHub
Actions, conforme validação informada pelo usuário. Os 195 testes desta etapa
ainda aguardam publicação e execução no GitHub Actions.

## Análise por mapa

```python
from src.mapas import obter_estatisticas_mapas, obter_melhor_mapa, obter_pior_mapa

mapas = obter_estatisticas_mapas(conn, player_id)
best = obter_melhor_mapa(conn, player_id)
worst = obter_pior_mapa(conn, player_id)
```

As três funções recebem `(conn: sqlite3.Connection, player_id: int)`.
A primeira retorna uma lista de dicionários classificados ou `[]` sem performances;
as outras retornam o primeiro/último dicionário ou `None`. Com um mapa, Best e
Worst coincidem. Cada dicionário contém `mapa`, `partidas`, `vitorias`, `derrotas`,
`empates`, `kd`, `kda`, `hs_percent`, `adr`, `kast_percent` e `win_rate`.

As fórmulas seguem `src/metricas.py`, aplicadas aos totais de cada mapa:
K/D = kills / max(1, deaths); KDA = (kills + assists) / max(1, deaths);
HS% = headshots / kills * 100 (0.0 sem kills); ADR = damage / rounds_played;
KAST% = kast_rounds / rounds_played * 100; Win Rate = vitorias / partidas * 100.
Empates e derrotas entram no denominador do Win Rate. Não há média simples das
métricas individuais nem arredondamento dentro das funções.

Classificação: Win Rate decrescente, ADR decrescente, K/D decrescente e nome
crescente. Best é o primeiro; Worst é o último, inclusive no desempate por nome.
Nomes são agrupados exatamente como armazenados; a ordem lexicográfica é
sensível a maiúsculas e minúsculas, sem normalização ou regras de idioma.
`partidas` contextualiza a amostra: não há mínimo obrigatório e amostras pequenas
podem produzir resultados pouco representativos.

Somente performances do jogador entram no resumo, via JOIN parametrizado.
As consultas não armazenam métricas nem executam commit, rollback ou close.
QA-INT-005 foi executado pelo usuário em 29/10/2026, às 14:47:48 (UTC−03:00),
e aprovado pelo QA Lead após revisão da captura. Os cinco cenários manuais
estão documentados em QA.md. Os 195 testes automatizados ainda não foram
validados no GitHub Actions.
