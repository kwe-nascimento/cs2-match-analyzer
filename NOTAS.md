# NOTAS - Analisador de Partidas CS2

## 🎯 Objetivo
Sistema em Python + SQL que registra minhas partidas de CS2 e calcula métricas de desempenho. Portfólio de QA.

## 📍 Onde estou
Schema SQL criado e testado (36 testes de regras de qualidade passando). Ainda sem inserção de dados nem métricas.
O primeiro commit foi realizado.

## ➡️ PRÓXIMO PASSO (só um!)
Rodar `pytest` na minha máquina e fazer o primeiro commit no GitHub.

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
1. Funções para inserir partida e performance (src/)
2. Métricas: K/D, KDA, HS%, ADR, KAST%, Win Rate
3. Desempenho por mapa + Best/Worst Map
4. CI com GitHub Actions
5. Plano de testes e modelo de bug report

## 💡 Ideias futuras (só anotar, NÃO fazer agora)
- Tabela ROUND
- Parsing de demos .dem

## ❓ Dúvidas abertas
Tinha muitas dúvidas quanto ao Git e GitHub, mas consegui sanar todas com ajuda de vídeos e I.A também.
