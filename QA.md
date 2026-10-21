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
![Evidência de execução — QA-INT-001](docs/evidencias/QA-INT-001.png)


## QA-INT-002 — Registro de transação válida

**Tipo:** Teste manual de integração  
**Prioridade:** Alta  
**Data:** 21/10/2026  
**Status:** PASSOU

### Objetivo
Verificar se uma partida e sua performance válida são registradas corretamente na mesma transação, garantindo a integridade dos dados e o relacionamento entre jogador, partida e performance.

### Pré-condições
- Banco SQLite de teste inicializado em memória.
- Jogador `jogador_teste` previamente cadastrado e confirmado com `commit()`.
- Funções `registrar_partida()` e `registrar_performance()` disponíveis.
- Conexão com o banco configurada com suporte a chaves estrangeiras.

### Procedimento
1. Inicializar o banco SQLite de teste em memória.
2. Cadastrar o jogador `jogador_teste` e confirmar seu registro.
3. Iniciar uma transação utilizando `with conn`.
4. Registrar uma partida válida no mapa Inferno (`de_inferno`), com vitória por 13×9.
5. Registrar uma performance associada ao jogador e à partida, contendo:
   - 20 kills.
   - 15 deaths.
   - 5 assists.
   - 10 headshots.
   - 22 rounds jogados.
6. Finalizar a transação sem provocar exceções.
7. Consultar a quantidade de registros existentes nas tabelas `player`, `partida` e `performance`.
8. Executar uma consulta SQL utilizando `JOIN` para verificar o relacionamento entre os registros.
9. Consultar `conn.in_transaction` para verificar se existe uma transação pendente.
10. Comparar os resultados obtidos com os resultados esperados.

### Resultado esperado
- A partida e a performance devem ser registradas sem erros.
- As funções devem retornar identificadores válidos.
- O banco deve conter um jogador, uma partida e uma performance.
- A performance deve estar corretamente associada ao jogador e à partida.
- A consulta SQL com `JOIN` deve retornar o jogador, o mapa e suas estatísticas corretamente.
- A transação deve ser finalizada sem operações pendentes.

### Resultado obtido
- Partida ID: `1`.
- Performance ID: `1`.
- Jogadores encontrados: `1`.
- Partidas encontradas: `1`.
- Performances encontradas: `1`.
- Resultado do JOIN: `('jogador_teste', 'de_inferno', 20, 15, 10)`.
- Transação aberta: `False`.
- Resultado apresentado no terminal: `RESULTADO: PASSOU`.

### Conclusão
**PASSOU.** O registro da partida e da performance foi realizado com sucesso. As consultas confirmaram a presença dos registros e o relacionamento correto entre as tabelas.

A execução demonstrou o funcionamento esperado da transação válida, sem erros de integridade ou registros inconsistentes no cenário testado.

**Limitação:** como o teste utilizou um banco SQLite em memória, não foi verificada a persistência dos dados após fechar e reabrir uma conexão com um banco em arquivo.

### Evidência
Reexecução manual realizada em 21/10/2026, às 16:34:38, com validação dos resultados pelo terminal Python.

![Evidência de execução — QA-INT-002](docs/evidencias/QA-INT-002.png)