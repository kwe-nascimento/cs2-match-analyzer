# NOTAS - Analisador de Partidas CS2

## 🎯 Objetivo
Sistema em Python + SQL que registra minhas partidas de CS2 e calcula métricas de desempenho. Portfólio de QA.

## 📍 Onde estou
- Modelagem inicial do banco de dados SQLite concluída.
- Schema SQL implementado com regras de integridade.
- 138 testes automatizados aprovados localmente com Pytest: 116 anteriores preservados e 22 novos testes de métricas.
- Validação desta atualização no GitHub Actions ainda não realizada.
- Quatro cenários de integração documentados; QA-INT-004 aprovado em 28/10/2026 às 18:39:17.
- Pipeline de CI configurado com GitHub Actions.
- Repositório publicado e versionado no GitHub.
- Registro de partidas implementado em `src/registros.py`.
- Registro de performances implementado em `src/registros.py`.
- Consulta do histórico implementada em `src/consultas.py`.
- Métricas individuais e acumuladas implementadas em `src/metricas.py`.
- Análises por mapa e interface gráfica pendentes.

## ➡️ PRÓXIMO PASSO
Desenvolver análises de desempenho por mapa como próxima funcionalidade,
incluindo Best/Worst Map.

Objetivos:
- Utilizar as tabelas e funções existentes.
- Manter os cálculos de métricas consistentes com as fórmulas implementadas.
- Criar testes para as análises por mapa e preservar os testes existentes.

Sempre desenvolvendo uma funcionalidade por vez,
compreendendo o código antes de avançar.

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
4. **Próxima funcionalidade:** desenvolver análises de desempenho por mapa, incluindo Best/Worst Map.
5. Criar um plano de testes documentando cenários positivos, negativos e valores-limite.
6. Elaborar um modelo de Bug Report para documentar defeitos encontrados.
7. Implementar uma interface gráfica simples com Streamlit para registrar partidas e visualizar estatísticas.
8. Desenvolver testes funcionais e de integração para validar os fluxos da aplicação.
9. Implementar gráficos e indicadores visuais para acompanhar a evolução do desempenho.
10. Adicionar relatórios de cobertura de testes com pytest-cov.
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
- A validação desta atualização no GitHub Actions ainda não foi realizada.
- Próxima funcionalidade: análises de desempenho por mapa, incluindo Best/Worst Map.
