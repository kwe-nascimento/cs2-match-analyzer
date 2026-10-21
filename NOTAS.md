# NOTAS - Analisador de Partidas CS2

## 🎯 Objetivo
Sistema em Python + SQL que registra minhas partidas de CS2 e calcula métricas de desempenho. Portfólio de QA.

## 📍 Onde estou
- Modelagem inicial do banco de dados SQLite concluída.
- Schema SQL implementado com regras de integridade.
- 36 testes automatizados passando com Pytest.
- Pipeline de CI configurado com GitHub Actions.
- Repositório publicado e versionado no GitHub.
- Registro de partidas implementado em `src/partidas.py`.
- Registro de performances implementado em `src/performances.py`.
- Consultas ainda não implementadas.
- Cálculo de métricas e interface gráfica pendentes.

## ➡️ PRÓXIMO PASSO
Revisar o registro de performances e consolidar o entendimento antes de
escolher a próxima funcionalidade.

Objetivos:
- Utilizar a conexão existente em src/db.py.
- Criar funções para inserir partidas.
- Criar funções para inserir performances.
- Respeitar as regras de integridade já implementadas.

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
1. Implementar funções para registrar e consultar partidas e performances (Python).
2. Criar testes automatizados para as funcionalidades de registro e consulta (Pytest).
3. Implementar consultas SQL para calcular K/D, KDA, HS%, ADR, KAST% e Win Rate.
4. Desenvolver análises de desempenho por mapa, incluindo Best/Worst Map.
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
