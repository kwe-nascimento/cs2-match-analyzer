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

O projeto possui **315 testes automatizados com Pytest aprovados localmente**
(260 anteriores preservados e 55 novos no seletor de mapas), além de **8 cenários
manuais documentados: 7 aprovados e QA-INT-008 aprovado com observações, com evidências**. O commit `289c378` também teve os 138 testes aprovados no GitHub Actions: [execução confirmada de 28/10/2026](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40775358994).

| ID | Cenário de integração | Resultado |
|---|---|---|
| **QA-INT-001** | Rejeição de performance inválida e rollback | **PASSOU** |
| **QA-INT-002** | Registro válido e verificação com SQL JOIN | **PASSOU** |
| **QA-INT-003** | Consulta de histórico, ordenação e isolamento entre jogadores | **PASSOU** |
| **QA-INT-004** | Validação das métricas de desempenho | **PASSOU** |
| **QA-INT-005** | Análise de desempenho por mapa e Best/Worst Map | **PASSOU** |
| **QA-INT-006** | Validação funcional da interface Streamlit e persistência | **PASSOU** |
| **QA-INT-007** | Evolução histórica, filtros, isolamento, atualização e persistência | **PASSOU** |
| **QA-INT-008** | Seleção controlada de mapas e integração | **APROVADO MANUALMENTE, COM OBSERVAÇÕES** |

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
Os 260 testes da evolução já foram aprovados remotamente, conforme informação do QA Lead. Os 315 testes do seletor foram aprovados localmente; sua execução remota está pendente.

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
e aprovado pelo QA Lead após revisão da captura. Os oito cenários manuais
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
partida, Histórico, Estatísticas por mapa e Evolução para acompanhar seus resultados.
O tema nativo é escuro, com grafite e azul, configurado em `.streamlit/config.toml`.

O formulário salva partida e performance juntas. Resultado e rounds jogados
são definidos pelo placar; erros de integridade não deixam partida incompleta.
No formulário, o mapa é escolhido explicitamente no seletor e salvo com ID
canônico. “Outro / Personalizado” permite texto com a normalização existente
e orientação para nomes parecidos com os mapas do catálogo. Consulte a seção
“Incremento — seleção controlada de mapas” abaixo. Registros antigos não são renomeados.

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
Actions conforme informação do QA Lead. A evolução com 260 testes foi aprovada remotamente, conforme informação do QA Lead.
O seletor tem 315 testes aprovados localmente e aguarda execução remota.


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
QA-INT-007 foi aprovado manualmente pelo QA Lead, com 15 capturas verificadas. A evolução com 260 testes já foi
aprovada remotamente, conforme informação do QA Lead neste fechamento. Nenhum staging, commit ou push.
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
aprovado no GitHub Actions, conforme informação do QA Lead. A evolução
com 260 testes foi aprovada remotamente, conforme informação do QA Lead.
O seletor tem 315 aprovados localmente e execução remota pendente.
Os 100% de cobertura referem-se apenas a `src/`, sem incluir `app.py`.

Melhorias futuras, sem implementação neste incremento:

- Atualizar a identificação antiga `MVP VISUAL 1` na sidebar.
- Ajustar escala e apresentação dos gráficos.
- Reformular visualmente o dashboard.

Próximo passo: revisão final e autorização do QA Lead antes de staging,
commit ou push. Relatórios locais e scripts `qa_evidencia_*.py` ficam fora
da lista recomendada de publicação; bancos SQLite também ficam de fora.

## Incremento — seleção controlada de mapas (2026-10-30)

Na aba **Registrar partida**, escolha explicitamente o **Mapa** antes de
preencher os demais dados. O seletor começa sem opção selecionada, inclusive
ao abrir “Registrar outra partida”. Salvar sem escolha exibe orientação e não
grava partida ou performance. O nome amigável é apresentado e o ID canônico
é salvo. O catálogo não depende da rotação Active Duty.

| Nome amigável | ID salvo |
| --- | --- |
| Mirage | de_mirage |
| Inferno | de_inferno |
| Nuke | de_nuke |
| Dust II | de_dust2 |
| Ancient | de_ancient |
| Anubis | de_anubis |
| Cache | de_cache |
| Train | de_train |
| Overpass | de_overpass |
| Vertigo | de_vertigo |
| Office | cs_office |

**Outro / Personalizado** revela o campo de texto correspondente. Entrada
vazia é rejeitada. Para um mapa customizado, a normalização existente continua:
minúsculas, espaços convertidos em `_`, prefixo `de_` quando não há `_`.
Exemplos: ` aim_custom ` → `aim_custom`; `Minha Arena` → `minha_arena`.
Nomes/IDs exatos de mapas do catálogo digitados nesse campo convergem ao ID
oficial: `Dust II` → `de_dust2`, `Office` → `cs_office`.

No formulário, a comparação ignora caixa, espaços, `_`, hífens e prefixo
`de_`/`cs_`. Uma aproximação com similaridade de pelo menos 0,8 por `difflib`
é bloqueada com sugestão clara para selecionar o mapa oficial; não é corrigida
silenciosamente. Exemplo: `mirrage` sugere Mirage. É uma heurística, sem
garantia de detectar todo erro; um nome customizado muito próximo de um mapa
do catálogo também pode ser bloqueado e precisa de nome distinto.

O catálogo central está em `src/catalogo_mapas.py`: para ampliá-lo, adicione
um par `(nome amigável, ID canônico)` a `CATALOGO_MAPAS`, mantendo IDs e nomes
únicos. `NOMES_MAPAS` deriva as opções do seletor; `OUTRO_MAPA` identifica
a opção personalizada. `resolver_mapa_formulario(selecao, personalizado="")`
retorna o valor para gravação ou lança `ValueError` com orientação.

Essa regra é exclusiva do formulário. A API e o comportamento de
`src/app_servicos.py` não mudaram: chamadas diretas continuam aceitando texto
livre e usando `normalizar_mapa`. Não há migração ou renomeação de registros
anteriores. Por exemplo, `dust_ii` legado permanece separado de `de_dust2`.
Schema, métricas, consultas, tema e evidências manuais existentes preservados.

O seletor fica antes do `st.form`, pois a escolha precisa disparar rerun para
mostrar/ocultar imediatamente o campo personalizado. Escolha o mapa primeiro:
alterar o seletor durante o preenchimento pode descartar valores ainda não
enviados pelo formulário. As chaves incluem jogador e geração do formulário,
para impedir reaproveitamento da escolha entre jogadores ou novos registros.

Validação local: **315 testes aprovados**, 260 anteriores e 55 novos
(34 casos do catálogo e 21 de interface). AppTest usa `CS2_DB_PATH` temporário;
nenhum teste acessa banco pessoal. Os testes anteriores de UI foram adaptados
ao seletor, preservando suas verificações funcionais. Cobertura apenas de
`src/`: **100%**, 158 statements e 46 branches; catálogo: 26 statements,
10 branches, 100%. `app.py` não está incluído nessa medição.

```powershell
python -B -m pytest -q -p no:cacheprovider
python -B -m pytest -q -p no:cacheprovider --cov=src --cov-branch --cov-report=term-missing
git diff --check
git status --short
```

Executados com `.venv/Scripts/python.exe` no Windows/Python 3.12.1.
O seletor foi aprovado manualmente no QA-INT-008, com observações.
A revisão documental final e a execução remota dos 315 testes permanecem pendentes. Sem novas dependências,
staging, commit ou push neste incremento. Base: `main`, `8ed917455d48586938c5b2eb69c1e74dd88fa6df`.

### Fechamento manual — QA-INT-008 (2026-10-30)

**APROVADO MANUALMENTE, COM OBSERVAÇÕES**. As nove capturas existentes estão
referenciadas nas seis etapas de [QA.md](QA.md#qa-int-008--seleção-controlada-de-mapas).
Confirmados seleção obrigatória, Inferno como `de_inferno`, rejeição de
`Ineferno`, custom `aim_custom` e integração com estatísticas/evolução.
O catálogo continua com 11 mapas; a prevenção de nomes semelhantes é
heurística e as regras/limitações descritas acima permanecem.

O jogador QA_MAPAS_A terminou com quatro partidas: `de_inferno`, `aim_custom`,
`de_mirage`, `de_nuke`. O testador relatou envio antecipado por Enter, deixando
Damage e KAST Rounds de aim_custom em zero; os dados foram preservados.
Na etapa de troca de mapa também houve envios acidentais. O testador informou
que repetiu o procedimento e os campos permaneceram preenchidos; o print do
histórico não comprova diretamente esse estado antes do envio. Não se oferece
garantia geral de preservação de valores ainda não enviados em todos os reruns.

Backlog, sem mudanças funcionais agora:

- Prevenir envio acidental do formulário por Enter.
- Avaliar confirmação dos dados antes da gravação.
- Prevenir registros incompletos sem proibir zeros legítimos.

Situação dos testes: **260 já aprovados remotamente**, conforme informação do
QA Lead; **315 aprovados localmente** na versão do seletor, revalidados neste
fechamento. **Execução remota dos 315 pendente**. Cobertura de 100% somente
em `src/`, 158 statements e 46 branches; `app.py` fora dessa medição.
Sem staging, commit ou push. Aguardar autorização do QA Lead.
