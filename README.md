# Analisador de Partidas de CS2

[![Testes automatizados](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml/badge.svg)](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/workflows/main.yml)

Projeto de estudo em **Python e SQLite**, com **Pytest** e GitHub Actions, para
registrar partidas de CS2 e o desempenho dos jogadores. O foco é praticar SQL,
qualidade de dados e testes automatizados.

O registro de partidas e performances, a consulta do histórico e as métricas de
desempenho, as análises por mapa e a interface local Streamlit estão implementados. O banco armazena somente dados brutos nas tabelas `player`, `partida` e
`performance`; as métricas são calculadas nas consultas.


O projeto permite registrar partidas, armazenar performances individuais
e consultar o histórico de partidas de um jogador, com ordenação
cronológica e validação de integridade no banco de dados.

As métricas K/D, KDA, HS%, ADR e KAST% estão implementadas por partida e no
resumo acumulado do jogador, que também inclui Win Rate. As análises por
mapa incluem Best/Worst Map e podem ser consultadas na interface gráfica local.

## Quality Assurance

O projeto possui **235 testes automatizados com Pytest aprovados localmente**
(195 anteriores preservados e 40 novos testes de serviços e interface), além de **6 cenários
manuais de integração documentados e aprovados, com evidências**. O commit `289c378` também teve os 138 testes aprovados no GitHub Actions: [execução confirmada de 28/10/2026](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40775358994).

| ID | Cenário de integração | Resultado |
|---|---|---|
| **QA-INT-001** | Rejeição de performance inválida e rollback | **PASSOU** |
| **QA-INT-002** | Registro válido e verificação com SQL JOIN | **PASSOU** |
| **QA-INT-003** | Consulta de histórico, ordenação e isolamento entre jogadores | **PASSOU** |
| **QA-INT-004** | Validação das métricas de desempenho | **PASSOU** |
| **QA-INT-005** | Análise de desempenho por mapa e Best/Worst Map | **PASSOU** |
| **QA-INT-006** | Validação funcional da interface Streamlit e persistência | **PASSOU** |

Os cenários verificam integridade de dados, transações, consultas SQL e métricas
de desempenho.
QA-INT-001 a QA-INT-005 foram executados por scripts Python iniciados manualmente,
com verificações por `assert`. QA-INT-006 foi executado no navegador pelo usuário,
incluindo persistência após reinicializar o Streamlit.

**[Consultar documentação completa, resultados e evidências](QA.md)**

## Instalação e testes

Na pasta do repositório, com Python 3.12:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

Os testes verificam regras do schema, registros válidos e inválidos,
relacionamentos, duplicatas, persistência, rollback, consultas do histórico
de partidas, cálculos individuais e acumulados de métricas, validade das datas
e consistência dos placares após atualização, agregação por mapa e classificação
Best/Worst Map, além de cadastro, persistência e fluxos de interface com AppTest.

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
Actions, conforme validação informada pelo usuário. A suíte atual de 235 testes
ainda aguarda publicação e execução no GitHub Actions.

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
e aprovado pelo QA Lead após revisão da captura. Os seis cenários manuais
estão documentados em QA.md. Os 235 testes desta etapa ainda não foram
validados no GitHub Actions. QA-INT-006 foi aprovado, incluindo os fluxos da interface e a persistência confirmada manualmente.

## Interface gráfica — MVP visual 1

Com Python 3.12, abra o PowerShell na raiz do repositório:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O Streamlit mostra o endereço local no terminal. Cadastre um jogador na barra
lateral (Steam ID opcional) e selecione-o. Use as abas Visão geral, Registrar
partida, Histórico e Estatísticas por mapa para acompanhar seus resultados.
O tema nativo é escuro, com grafite e azul, configurado em `.streamlit/config.toml`.

O formulário salva partida e performance juntas. Resultado e rounds jogados
são definidos pelo placar; erros de integridade não deixam partida incompleta.
O nome do mapa vira minúsculas, espaços viram `_` e nomes sem `_` recebem `de_`:
Mirage, mirage e de_mirage ficam como de_mirage. Nomes personalizados com prefixo,
como aim_custom e cs_office, são preservados após essa normalização. Registros
antigos não são renomeados automaticamente.

Após salvar, clique em **Registrar outra partida** para abrir um formulário novo.
Reruns não repetem a gravação. Essa proteção é temporária por sessão; reenviar
manualmente dados iguais em uma nova sessão ou outro formulário cria uma nova
partida. Não há deduplicação global por conteúdo, pois partidas iguais podem
ser legítimas.

Os dados ficam em `data/cs2.sqlite`, relativo à raiz do projeto, independentemente
do diretório do terminal. A pasta é criada automaticamente. Cada execução abre
e fecha sua própria conexão; nenhuma conexão global é compartilhada entre sessões.
Para um banco alternativo, antes de iniciar:

```powershell
$env:CS2_DB_PATH = 'C:\caminho\alternativo\cs2.sqlite'
python -m streamlit run app.py
```

Caminhos relativos em `CS2_DB_PATH` também partem da raiz do projeto. Arquivos
SQLite são ignorados pelo Git. Os testes novos usam `tmp_path` e `CS2_DB_PATH`
para nunca acessar os dados reais.

```powershell
python -B -m pytest -q -p no:cacheprovider
python -B -m pytest -q -p no:cacheprovider --cov=src --cov-branch --cov-report=term-missing
# Medição separada da UI, pois app.py está fora de src:
python -B -m pytest -q -p no:cacheprovider tests/test_app_servicos.py tests/test_app_streamlit.py --cov=src.app_servicos --cov=app --cov-branch --cov-report=term-missing
```

Resultados locais: 235 testes aprovados, 100% de cobertura em src e 98% em app.py
na medição separada da interface. A validação funcional no navegador foi concluída
e aprovada no QA-INT-006; a cobertura automatizada é uma verificação separada.

Limitações: aplicativo local sem login; não há edição, exclusão, importação da
Steam ou hospedagem pública. A seleção de jogador organiza os dados, sem oferecer
controle de acesso. Gravações SQLite concorrentes podem exigir nova tentativa.
Best/Worst Map continua sem mínimo de partidas: amostras pequenas podem ser pouco
representativas. A publicação e a validação dos 235 testes no GitHub Actions permanecem pendentes.
