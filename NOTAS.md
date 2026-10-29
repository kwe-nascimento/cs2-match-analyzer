# NOTAS - Analisador de Partidas CS2

## 🎯 Objetivo
Sistema em Python + SQL que registra minhas partidas de CS2 e calcula métricas de desempenho. Portfólio de QA.

## 📍 Onde estou
- Modelagem inicial do banco de dados SQLite concluída.
- Schema SQL implementado com regras de integridade.
- 237 testes automatizados aprovados localmente: 235 anteriores preservados e duas novas regressões transacionais. Manutenção ainda não publicada nem executada remotamente.
- MVP Visual 1 publicado no commit `6a8d43d`: 235 testes aprovados no GitHub Actions, Linux/Python 3.12.15, src com 100% (106 statements e 26 branches); [execução remota aprovada](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40942192660).
- Base `0c17c96`: 167 testes e 100% de cobertura Python aprovados no GitHub Actions, conforme validação informada pelo usuário. A suíte atual da manutenção (237 testes locais) aguarda publicação e execução remota.
- Commit `289c378`: 138 testes aprovados no GitHub Actions; [execução confirmada de 28/10/2026](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40775358994).
- Seis cenários manuais de integração documentados e aprovados; QA-INT-006 concluído pelo usuário em 29/10/2026, incluindo persistência após reinicializar o Streamlit. QA-INT-005 preservado com sua execução em 29/10/2026 às 14:47:48 (UTC−03:00).
- Cobertura local desta manutenção: src com 100% (108 statements, 28 branches); app.py com 98% na medição separada da validação local anterior.
- Pipeline de CI configurado com GitHub Actions.
- Repositório publicado e versionado no GitHub.
- Registro de partidas implementado em `src/registros.py`.
- Registro de performances implementado em `src/registros.py`.
- Consulta do histórico implementada em `src/consultas.py`.
- Métricas individuais e acumuladas implementadas em `src/metricas.py`.
- Análises por mapa e Best/Worst Map implementados; interface local Streamlit disponível em `app.py`.

## ➡️ PRÓXIMO PASSO
MVP visual 1 publicado em `6a8d43d` e aprovado remotamente com 235 testes.
Aguardar revisão do QA Lead para publicar a manutenção transacional/Actions,
validada com 237 testes locais; sem commit ou push nesta sessão.

## ✅ Decisões tomadas (não rediscutir)
- Banco guarda só dados brutos; métricas são calculadas depois
- 3 entidades: PLAYER, PARTIDA, PERFORMANCE
- PERFORMANCE liga jogador e partida (UNIQUE player + partida)
- KAST = campo kast_rounds por partida (por round fica pro futuro)
- IC (inimigos cegados) é separado de flash assists
- Só analiso o meu desempenho no MVP
- Banco: SQLite

## 🧪 Regras de qualidade (já viraram CHECK/trigger + testes)
- headshots <= kills; first_kills <= kills; first_deaths <= deaths
- kast_rounds <= rounds_played
- first_kills + first_deaths <= rounds_played
- rounds_played > 0 e igual ao placar da partida
- resultado coerente com o placar
- sem valores negativos; data em AAAA-MM-DD

## 🗺️ Próximas etapas (em ordem)
1. **Concluído:** implementar funções para registrar partidas e performances e consultar o histórico (Python).
2. **Concluído:** criar testes automatizados para registro e consulta (Pytest).
3. **Concluído:** implementar métricas K/D, KDA, HS%, ADR, KAST% e Win Rate, com testes.
4. **Implementado e validado no QA-INT-005:** análises de desempenho por mapa, incluindo Best/Worst Map; publicado antes desta manutenção.
5. Criar um plano de testes documentando cenários positivos, negativos e valores-limite.
6. Elaborar um modelo de Bug Report para documentar defeitos encontrados.
7. **Implementado e validado no QA-INT-006:** MVP visual 1 com Streamlit para cadastro, registro e estatísticas; publicado em `6a8d43d`.
8. Desenvolver testes funcionais e de integração para validar os fluxos da aplicação.
9. Implementar gráficos e indicadores visuais para acompanhar a evolução do desempenho.
10. **Concluído:** cobertura com pytest-cov; manutenção `0c17c96` aprovada remotamente com 167 testes e 100% de cobertura Python.
11. Aprimorar a documentação do projeto com exemplos de utilização e resultados dos testes.

### ✅ Etapas concluídas
- Modelagem inicial do banco de dados SQLite.
- Implementação de regras de integridade e validação dos dados.
- Criação de 36 testes automatizados com Pytest.
- Configuração de CI com GitHub Actions.
- Execução bem-sucedida dos 36 testes no GitHub Actions.

## 💡 Ideias futuras (só anotar, NÃO fazer agora)
- Tabela ROUND
- Parsing de demos .dem

## Registro de partidas — 2026-10-21

- `registrar_partida` recebe uma conexão existente e os cinco campos da partida.
- SQL parametrizado; validação delegada ao schema; exceções SQLite propagadas.
- Retorna `lastrowid`; commit, rollback e fechamento ficam com o chamador.
- 27 novos casos de teste, incluindo persistência em arquivo, rollback e texto SQL literal.
- Validação local: `python -B -m pytest -q -p no:cacheprovider`: 63 testes passando,
  incluindo os 36 originais, preservados sem alterações.
- Schema preservado; performances aguardam autorização.

Observações fora do escopo, sem correções nesta etapa:
- O CHECK da data verifica o formato, mas não a validade no calendário.
- Há arquivos `__pycache__` versionados, que podem mudar ao executar Python.

## Registro de performances — 2026-10-21

- Implementado após autorização da etapa seguinte pelo usuário.
- `registrar_performance` recebe conexão, IDs existentes e os 12 campos brutos.
- Parâmetros após a conexão são passados por nome para evitar troca de estatísticas.
- SQL parametrizado; validação pelo schema; erros SQLite propagados.
- Retorna `lastrowid`; transação e fechamento controlados pelo chamador.
- 45 novos casos de teste: associação, dados persistidos, limites, negativos,
  campos obrigatórios, duplicatas, IDs inexistentes, rounds, rollback e reabertura.
- Validação: `python -B -m pytest -q -p no:cacheprovider`: 108 testes passando
  (36 originais + 27 de partidas + 45 de performances).
- Schema e testes anteriores preservados; nenhuma métrica ou nova tabela criada.
- Preferência de entrega: incluir arquivo `.txt` com código e alterações destacadas
  ao concluir cada operação.

## 📚 Aprendizados recentes
- Criação e organização de repositórios no GitHub.
- Utilização de commits para versionamento.
- Configuração de workflows com GitHub Actions.
- Identificação e correção de erros em pipelines de CI.
- Execução automatizada de testes com Pytest.

## ❓ Dúvidas abertas
- Como estruturar as funções de inserção e consulta de dados?
- Como organizar os testes das novas funcionalidades?

## Organização dos módulos — 2026-10-21

- As duas funções de registro foram reunidas em `src/registros.py`.
- `src/db.py` continua responsável pela conexão e inicialização do banco.
- Os testes permanecem separados por funcionalidade; apenas seus imports mudaram.
- Assinaturas, SQL, validações e controle das transações foram preservados.
- README simplificado para objetivo, uso, testes e estrutura.
- Relatórios anteriores preservados como histórico da organização daquela etapa.

## Métricas de desempenho — 2026-10-28

- `obter_metricas_partida(conn, player_id, partida_id)` retorna `kd`, `kda`,
  `hs_percent`, `adr` e `kast_percent`, ou `None` sem performance associada.
- `obter_resumo_jogador(conn, player_id)` retorna contagens de partidas,
  vitórias, derrotas e empates, as cinco métricas e `win_rate`; retorna `None`
  quando não há partidas associadas ao jogador.
- Fórmulas:
  - K/D = `kills / max(1, deaths)`.
  - KDA = `(kills + assists) / max(1, deaths)`.
  - HS% = `headshots / kills * 100`; quando kills é zero, retorna `0.0`.
  - ADR = `damage / rounds_played`.
  - KAST% = `kast_rounds / rounds_played * 100`.
  - Win Rate = `vitorias / partidas * 100`, incluindo derrotas e empates no denominador.
- No resumo, as razões usam os totais acumulados, nunca a média simples das
  razões individuais; a convenção de zero mortes é aplicada ao total de deaths.
- Os resultados não são arredondados; a apresentação fica a cargo da interface.
- SQL parametrizado e consultas sem alteração de registros; transações e
  fechamento da conexão continuam sob responsabilidade do chamador.
- 22 novos testes de integração de métricas em SQLite em memória, com
  `pytest.approx` para comparações decimais. Os 116 testes anteriores foram preservados.
- Validação local: `python -B -m pytest -q -p no:cacheprovider`: **138 testes aprovados**.
- QA-INT-004 aprovado em **28/10/2026 às 18:39:17**; evidência em
  [QA-INT-004](docs/evidencias/QA-INT-004.png) e cenário documentado em [QA.md](QA.md).
- Commit `289c378`: 138 testes aprovados no GitHub Actions; [execução confirmada de 28/10/2026](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40775358994).
- Próxima funcionalidade: análises de desempenho por mapa, incluindo Best/Worst Map.

## Manutenção de integridade — 2026-10-29

- Triggers de calendário em INSERT e UPDATE rejeitam datas inexistentes,
  formatos inválidos e ano 0000, incluindo retornos NULL do SQLite.
- Trigger de placar impede mudanças do total quando existe performance
  incompatível; preserva mudanças de soma igual e partidas sem performance.
- `init_db()` instala os triggers também em bancos existentes, sem recriar
  tabelas, duplicar triggers ou alterar registros legados. Dados antigos
  inválidos não são auditados nem corrigidos automaticamente.
- Caches retirados apenas do índice, com cópias locais preservadas; .gitignore,
  nomes de __init__ corrigidos e workflow redundante removido.
- pytest-cov mede linhas e branches, exibindo linhas não cobertas, sem limite
  mínimo obrigatório. HTML local em htmlcov/ ignorado pelo Git.
- Regressões cobrem calendário, preservação após rejeição, placares com um e
  dois jogadores, inicialização repetida e atualização de banco existente.
- A manutenção do commit `0c17c96` foi aprovada no GitHub Actions com 167 testes
  e 100% de cobertura Python. Naquela etapa, Best/Worst Map e Streamlit eram futuros.

## Análise por mapa — 2026-10-29

- `obter_estatisticas_mapas(conn, player_id)` retorna lista de resumos por mapa
  em ordem de classificação; `obter_melhor_mapa` e `obter_pior_mapa` recebem os
  mesmos argumentos e retornam o primeiro/último resumo ou None. Sem dados,
  a lista é vazia; com um mapa, Best e Worst coincidem.
- Resumos incluem mapa, partidas, vitórias, derrotas, empates e seis métricas.
- Fórmulas sobre totais por mapa, preservando `src/metricas.py`:
  K/D = kills / max(1, deaths); KDA = (kills + assists) / max(1, deaths);
  HS% = headshots / kills * 100, ou 0.0 sem kills; ADR = damage / rounds_played;
  KAST% = kast_rounds / rounds_played * 100; Win Rate = vitorias / partidas * 100.
  Sem média simples, arredondamento ou armazenamento de métricas no banco.
- Win Rate, ADR e K/D decrescentes; nome crescente como desempate final.
  Worst é o último inclusive no empate total. Nomes não são normalizados;
  agrupamento exato e ordem lexicográfica sensível a caixa.
- Sem mínimo de partidas. A contagem acompanha cada resumo; amostras pequenas
  podem ser pouco representativas.
- JOIN entre performance e partida, filtro parametrizado por jogador; partidas
  sem performance dele não entram. Consultas não controlam transações/conexão.
- 28 novos testes; 195 aprovados localmente. Cobertura Python: 100% em todos os
  módulos, 46 statements e 6 branches; 167 testes anteriores preservados.
- QA-INT-005 executado pelo usuário em 29/10/2026 às 14:47:48 (UTC−03:00),
  aprovado pelo QA Lead após revisão da captura; cinco cenários manuais
  documentados e aprovados. Evidência: [QA-INT-005](docs/evidencias/QA-INT-005.png).
- Resultado remoto da base 0c17c96 informado pelo usuário: 167 testes e 100%
  de cobertura. Esta nova etapa ainda não foi executada no GitHub Actions.
- Sem alterações de schema, fórmulas anteriores, dependências ou Streamlit.

## Interface Streamlit — MVP visual 1 — 2026-10-29

- `app.py` usa componentes nativos em quatro abas, com cadastro/seleção lateral,
  dashboard, registro, histórico e Best/Worst Map. Tema escuro em config.toml.
- `src/app_servicos.py` separa conexão, cadastro, normalização de mapa, validação
  amigável e gravação atômica da UI, permitindo testar rollback sem Streamlit.
- Caminho estável ROOT/data/cs2.sqlite, sobrescrito por CS2_DB_PATH; pais criados
  automaticamente. Conexão por execução com fechamento em finally, sem cache global.
- Cadastro parametrizado, nickname obrigatório, Steam ID vazio vira NULL;
  conflitos UNIQUE apresentados de forma amigável, sem traceback SQL na tela.
- Partida e performance passam pelas funções existentes em uma transação;
  resultado e rounds_played derivados do placar. SQLite mantém a proteção final.
- Normalização: minúsculas, espaços para _, prefixo de_ em nomes simples;
  mapas personalizados aceitos, sem migração dos nomes legados.
- Formulários gravam só no submit. Após sucesso, ficam substituídos pela confirmação
  até a ação Registrar outra partida; novo formulário tem chaves novas. Seleção e
  mensagens são temporárias no session_state; dados persistentes ficam no SQLite.
- Consultas sem cache usam módulos existentes; precisão e classificação preservadas.
- 40 novos casos cobrem serviços e AppTest. Suíte completa: 235 aprovados;
  src com 100%; UI app.py com 98% na medição separada (linhas 95–96 não cobertas,
  tratamento defensivo de rejeição do banco após a validação do formulário).
  Branch de importação do bloco __main__ também não percorrido na alternativa.
- Instalação de requirements concluída com Streamlit 1.66.1. Nenhum framework
  adicional foi adicionado diretamente; dependências transitivas vêm do Streamlit.
- Servidor iniciado apenas em localhost no teste: HTTP 200 na raiz e no health;
  processo encerrado. Fluxos funcionais passaram no AppTest e foram posteriormente
  aprovados na validação manual QA-INT-006.
- Problemas/limitações: não há deduplicação entre sessões ou formulários novos;
  SQLite pode ter contenção de escrita; não há autenticação, edição, exclusão,
  importação externa ou hospedagem. Nenhum erro bloqueante nos testes executados.
- Revisão técnica e validação manual QA-INT-006 concluídas e aprovadas.
  Publicação concluída em `6a8d43d`; 235 testes e 100% de cobertura em src
  aprovados no GitHub Actions.
  Cinco cenários anteriores preservados; total atual de seis aprovados.

## Conclusão do QA-INT-006 — 2026-10-29

- Validação manual da interface aprovada pelo usuário e pelo QA Lead: cadastro e
  seleção, nickname duplicado, registro, métricas individuais/acumuladas, mapas,
  histórico, isolamento e persistência após reiniciar o Streamlit.
- QA_TESTE_A: duas partidas (vitória e derrota), K/D 1,20, KDA 1,52, ADR 80,
  HS% 40%, KAST% 62,50% e Win Rate 50%.
- Sete capturas oficiais verificadas e referenciadas por etapa em QA.md.
  A imagem TESTEPERSISTIDO é complementar ao relato manual de reinicialização;
  não prova isoladamente a sequência. Isolamento sem captura independente.
- 235 testes locais aprovados. Cobertura informada no relatório: src com 100%
  (106 statements e 26 branches); app.py com 98% na medição separada da UI,
  com linhas 95–96 e alternativa do bloco __main__ não cobertas.
- Os 235 testes foram posteriormente aprovados no GitHub Actions no commit
  `6a8d43d`; [execução remota aprovada](https://github.com/kwe-nascimento/cs2-match-analyzer/actions/runs/40942192660).
- Limitações preservadas: versão local sem autenticação, edição/exclusão ou
  importação; proteção de duplicação temporária por sessão, sem deduplicação
  global; possível contenção de escrita SQLite; amostras pequenas por mapa.

### Backlog técnico — não bloqueia o MVP atual

- **Concluído nesta manutenção:** revisar o controle transacional de cadastrar_jogador() para evitar confirmar transações anteriores do chamador, com teste de regressão.

A melhoria foi apenas registrada na finalização documental anterior; sua implementação
e as duas regressões correspondentes foram concluídas na manutenção abaixo.

## Manutenção final do MVP Visual 1 — 2026-10-29

- Base `6a8d43d`: MVP publicado, 235 testes aprovados remotamente em Linux com
  Python 3.12.15 e src com 100% (106 statements, 26 branches). Sem hospedagem pública.
- `cadastrar_jogador()` agora rejeita conexão com transação anterior pendente
  antes de entrar em with conn. ValueError preserva os dados pendentes e a
  transação aberta; o chamador decide commit/rollback. Cadastro normal e
  rollback de duplicidade próprios preservados.
- Duas regressões: transação pendente sem confirmação/reversão indevida, incluindo
  observador independente e rollback do chamador; cadastro normal persistido
  após reabertura. Os 235 testes anteriores e testes AppTest foram preservados.
- Actions atualizadas para checkout@v7 e setup-python@v7. Metadados oficiais
  confirmam node24; configurações de runner ubuntu-latest, Python 3.12,
  eventos, dependências e pytest-cov preservadas. YAML analisado com parser.
- Validação local: 237 testes aprovados; src com 100%, 108 statements e 28 branches.
  A manutenção ainda aguarda publicação/CI; YAML válido não prova a execução das
  Actions. A ausência do aviso de Node.js 20 será conferida nos próximos logs.
- Seis cenários manuais e suas evidências preservados integralmente; sem QA-INT-007.
- Nenhuma nova dependência, tela, métrica ou alteração visual. Sem commit ou push.
