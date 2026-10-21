# Registro de testes — CS2 Match Analyzer

## QA-INT-001 — Integridade de transação

**Tipo:** Teste manual de integração  
**Prioridade:** Alta  
**Data:** 21/10/2026  
**Status:** PASSOU

### Objetivo
Verificar se uma falha ao registrar uma performance provoca o rollback da partida inserida na mesma transação.

### Pré-condições
- Banco SQLite de teste inicializado em memória.
- Jogador cadastrado e confirmado com `commit()`.
- Funções `registrar_partida()` e `registrar_performance()` disponíveis.

### Procedimento
1. Registrar uma partida válida na Mirage, com vitória por 13×7.
2. Tentar registrar uma performance com 5 kills e 6 headshots.
3. Capturar a exceção `sqlite3.IntegrityError`.
4. Consultar as tabelas após o rollback.

### Resultado esperado
- A performance inválida deve ser rejeitada.
- A partida não deve permanecer registrada.
- O jogador previamente confirmado deve permanecer no banco.

### Resultado obtido
- Exceção: `CHECK constraint failed: headshots <= kills`.
- Jogadores encontrados: 1.
- Partidas encontradas: 0.
- Performances encontradas: 0.

### Conclusão
**PASSOU.** O fluxo de transação apresentou o comportamento esperado, sem persistência parcial dos registros testados.

### Evidência
Saída do console Python verificada durante a execução manual. Captura de tela a anexar, caso disponível.

## QA-INT-002 — Registro de transação válida

**Tipo:** Teste manual de integração  
**Prioridade:** Alta  
**Data:** 21/10/2026  
**Status:** PASSOU

### Objetivo
Verificar se uma partida e sua performance válida são registradas corretamente na mesma transação, mantendo o relacionamento com o jogador.

### Pré-condições
- Banco SQLite em memória inicializado.
- Jogador `jogador_teste`, ID 1, previamente cadastrado.
- Funções de registro disponíveis.

### Procedimento
1. Registrar partida na Inferno, com vitória por 13×9.
2. Registrar performance de 20 kills, 15 deaths, 5 assists e 10 headshots.
3. Finalizar a transação com `with conn`.
4. Consultar as quantidades de registros.
5. Executar um `JOIN` para validar o relacionamento.
6. Verificar `conn.in_transaction`.

### Resultado esperado
- Um jogador, uma partida e uma performance.
- Performance associada ao jogador e mapa corretos.
- Transação encerrada sem erros.

### Resultado obtido
- Jogadores: 1.
- Partidas: 1.
- Performances: 1.
- Partida ID: 1.
- Performance ID: 1.
- JOIN: `('jogador_teste', 'de_inferno', 20, 15, 10)`.
- `conn.in_transaction`: `False`.

### Conclusão
**PASSOU.** As duas inserções foram executadas com sucesso e o relacionamento entre as tabelas foi confirmado.

**Evidência:** saída do console Python apresentada durante a execução manual.

**Limitação:** não foi testada a persistência após fechamento e reabertura de um banco em arquivo.