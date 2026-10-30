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

O MVP Visual 1 foi publicado no commit `6a8d43d`, com **235 testes aprovados no GitHub Actions** (Linux, Python 3.12.15) e **100% de cobertura em `src/`**: [execução remota aprovada](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40942192660). Foram cobertos 106 statements e 26 branches. A interface continua sendo um aplicativo local, sem hospedagem pública.

A manutenção anterior possui **237 testes aprovados localmente** (235 anteriores e 2 novas regressões transacionais), com 100% de cobertura em `src/` (108 statements e 28 branches). Essa manutenção já foi publicada e aprovada no GitHub Actions, conforme informação do QA Lead.

O projeto possui **260 testes automatizados com Pytest aprovados localmente**
(237 anteriores preservados e 23 novos), além de **7 cenários
manuais de integração documentados e aprovados, com evidências**. O commit `289c378` também teve os 138 testes aprovados no GitHub Actions: [execução confirmada de 28/10/2026](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40775358994).

| ID | Cenário de integração | Resultado |
|---|---|---|
| **QA-INT-001** | Rejeição de performance inválida e rollback | **PASSOU** |
| **QA-INT-002** | Registro válido e verificação com SQL JOIN | **PASSOU** |
| **QA-INT-003** | Consulta de histórico, ordenação e isolamento entre jogadores | **PASSOU** |
| **QA-INT-004** | Validação das métricas de desempenho | **PASSOU** |
| **QA-INT-005** | Análise de desempenho por mapa e Best/Worst Map | **PASSOU** |
| **QA-INT-006** | Validação funcional da interface Streamlit e persistência | **PASSOU** |
| **QA-INT-007** | Evolução histórica, filtros, isolamento, atualização e persistência | **PASSOU** |

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
pelo Git. O workflow já exibe cobertura nos logs; a atualização das Actions da
manutenção anterior já foi publicada e aprovada, conforme informação do QA Lead.
A base `0c17c96` teve 167 testes e 100% de cobertura Python aprovados no GitHub
Actions, conforme validação informada pelo usuário. O MVP Visual 1 (`6a8d43d`)
também foi aprovado remotamente com 235 testes. Os 237 testes da manutenção
anterior já foram aprovados no GitHub Actions, conforme informação do QA Lead.
Os 260 testes do incremento atual foram aprovados localmente; sua execução remota está pendente.

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
e aprovado pelo QA Lead após revisão da captura. Os sete cenários manuais
estão documentados em QA.md. Os 235 testes do MVP foram aprovados no GitHub
Actions; as duas regressões da manutenção também já foram aprovadas remotamente, totalizando 237, conforme informação do QA Lead. QA-INT-006 foi aprovado, incluindo os fluxos da interface e a persistência confirmada manualmente.

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

Resultados locais da manutenção anterior: 237 testes aprovados e 100% de cobertura em
src. A cobertura de app.py foi de 98% na medição separada da validação local anterior. A validação funcional no navegador foi concluída
e aprovada no QA-INT-006; a cobertura automatizada é uma verificação separada.

Limitações: aplicativo local sem login; não há edição, exclusão, importação da
Steam ou hospedagem pública. A seleção de jogador organiza os dados, sem oferecer
controle de acesso. Gravações SQLite concorrentes podem exigir nova tentativa.
Best/Worst Map continua sem mínimo de partidas: amostras pequenas podem ser pouco
representativas. O MVP e sua manutenção foram publicados, com 237 testes aprovados no GitHub
Actions conforme informação do QA Lead. O incremento atual tem 260 testes
aprovados localmente e aguarda execução remota.


## MVP Visual 2 — Incremento 1: evolução histórica (2026-10-30)

A aba **Evolução** apresenta K/D, ADR e KAST% por partida, em ordem de data
crescente e, em datas iguais, ID crescente. O eixo horizontal usa o número
sequencial da partida filtrada; a tabela auxiliar identifica ID, data, mapa,
resultado e valores. Os três gráficos usam `st.line_chart`, com azul explícito,
preservando o tema existente e sem dependências adicionais.

Filtros: Todos ou um mapa registrado pelo jogador, data inicial e final
inclusivas. Os padrões abrangem todo o histórico. Intervalo invertido ou data
ausente recebe orientação; filtros sem resultados e jogador sem partidas têm
mensagens próprias. Uma partida mostra valores e tabela, com aviso de que não
permite inferir tendência, sem traçar uma linha de evolução.

Os indicadores são razões dos totais filtrados: kills / max(1, deaths),
damage / rounds_played e kast_rounds / rounds_played * 100. Não são médias
das métricas individuais. Backend sem arredondamento; indicadores com duas
casas na apresentação. O schema garante rounds_played > 0.

API: `src.evolucao.listar_evolucao(conn, player_id, mapa=None,
data_inicial=None, data_final=None)` retorna lista de dicionários com dados
brutos e métricas; datas aceitam `date` ou strings ISO YYYY-MM-DD. Mapa usa
igualdade exata; `None` omite filtros opcionais. Intervalo invertido retorna
lista vazia. `resumir_evolucao(registros)` retorna indicadores agregados ou
`None` sem registros. Consultas parametrizadas, sem escrita ou controle da
conexão/transação. Validação de formato de datas externas cabe ao chamador.

Não há cache de consultas: reruns refletem novos registros. Filtros têm chaves
por jogador e assinatura do histórico; novo registro restaura os padrões para
incluir todo o histórico. Ao alternar jogadores os filtros não se misturam;
o Streamlit pode descartar o estado de widgets que deixam de ser renderizados.

Validação **local**, Windows/Python 3.12.1: 260 testes aprovados (237 anteriores
e 23 novos), com bancos temporários. Os testes incluem AppTest, filtros,
precisão, isolamento, SQL parametrizado, preservação da transação e reruns.
Cobertura de `src`: 100%, 132 statements, 36 branches; `evolucao.py`: 100%,
24 statements, 8 branches. Essa medição não inclui `app.py`.
Comandos executados:

```powershell
python -B -m pytest -q -p no:cacheprovider
python -B -m pytest -q -p no:cacheprovider --cov=src --cov-branch --cov-report=term-missing
git diff --check
git status --short
```

Foi usado o Python do ambiente `.venv/Scripts/python.exe` do projeto.
QA-INT-007 foi aprovado manualmente pelo QA Lead, com 15 capturas verificadas. Este incremento ainda não foi
validado remotamente no GitHub Actions. Nenhum staging, commit ou push.
Limitações: séries descritivas, sem inferência estatística, suavização,
paginação ou teste de carga; a consulta inicial carrega o histórico completo
para montar filtros. Nomes dos mapas seguem os valores armazenados.
Avisos de depreciação de `use_container_width` no Streamlit permanecem no
aplicativo existente; não foi realizada migração visual ampla.

### Fechamento do QA-INT-007 e backlog

QA-INT-007 **aprovado manualmente**, com 15 capturas existentes verificadas em
[QA.md](QA.md#qa-int-007--evolução-histórica-do-mvp-visual-2-incremento-1).
A reinicialização do Streamlit foi informada pelo testador; as capturas
posteriores mostram os dados. O histórico de 237 testes já foi publicado e
aprovado no GitHub Actions, conforme informação do QA Lead. O incremento
atual tem 260 testes aprovados **localmente**, conforme validação anterior e
revalidação deste fechamento; execução remota dos 260 ainda pendente.
Os 100% de cobertura referem-se apenas a `src/`, sem incluir `app.py`.

Melhorias futuras, sem implementação neste incremento:

- Atualizar a identificação antiga `MVP VISUAL 1` na sidebar.
- Ajustar escala e apresentação dos gráficos.
- Reformular visualmente o dashboard.

Próximo passo: revisão final e autorização do QA Lead antes de staging,
commit ou push. Relatórios locais e scripts `qa_evidencia_*.py` ficam fora
da lista recomendada de publicação; bancos SQLite também ficam de fora.
