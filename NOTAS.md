# NOTAS - Analisador de Partidas CS2

## 🎯 Objetivo
Sistema em Python + SQL que registra minhas partidas de CS2 e calcula métricas de desempenho. Portfólio de QA.

## 📍 Onde estou
- Modelagem inicial do banco de dados SQLite concluída.
- Schema SQL implementado com regras de integridade.
- 36 testes automatizados passando com Pytest.
- Pipeline de CI configurado com GitHub Actions.
- Repositório publicado e versionado no GitHub.
- Funcionalidades de registro e consulta de partidas ainda não implementadas.
- Cálculo de métricas e interface gráfica pendentes.

## ➡️ PRÓXIMO PASSO
Implementar as primeiras funções Python para registrar partidas
e performances no banco de dados SQLite.

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

## 📚 Aprendizados recentes
- Criação e organização de repositórios no GitHub.
- Utilização de commits para versionamento.
- Configuração de workflows com GitHub Actions.
- Identificação e correção de erros em pipelines de CI.
- Execução automatizada de testes com Pytest.

## ❓ Dúvidas abertas
- Como estruturar as funções de inserção e consulta de dados?
- Como organizar os testes das novas funcionalidades?
