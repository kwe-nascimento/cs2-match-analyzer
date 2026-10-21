# Registro de Testes — CS2 Match Analyzer

Documentação dos testes de integração executados no projeto **CS2 Match Analyzer**, desenvolvido com Python e SQLite.

Os cenários verificam a integridade dos dados, o gerenciamento de transações e os relacionamentos entre as tabelas do banco de dados.

## Resumo das execuções

| ID | Cenário | Natureza | Resultado |
|---|---|---|---|
| QA-INT-001 | Integridade de transação (rollback) | Negativo | PASSOU |
| QA-INT-002 | Registro de transação válida (commit) | Positivo | PASSOU |

**Ambiente de teste:** Python 3.12 e SQLite em memória.

**Método de execução:** cenários inicialmente executados de forma interativa no console Python e posteriormente reproduzidos por scripts Python iniciados manualmente, com verificações automatizadas por `assert`.

---

## QA-INT-001 — Integridade de transação

**Tipo:** Teste de integração — cenário negativo

**Prioridade:** Alta

**Data:** 21/10/2026

**Status:** PASSOU

### Objetivo

Verificar se uma falha ao registrar uma performance provoca o rollback da partida inserida na mesma transação, impedindo a persistência parcial dos registros.

### Pré-condições

- Banco SQLite de teste inicializado em memória.
- Jogador `jogador_teste` previamente cadastrado e confirmado com `commit()`.
- Funções `registrar_partida()` e `registrar_performance()` disponíveis.
- Regras de integridade do banco de dados habilitadas.

### Procedimento

1. Inicializar o banco SQLite em memória.
2. Cadastrar o jogador `jogador_teste` e confirmar seu registro.
3. Iniciar uma transação utilizando `with conn`.
4. Registrar uma partida válida no mapa Mirage (`de_mirage`), com vitória por 13×7.
5. Tentar registrar uma performance inválida contendo 5 kills e 6 headshots.
6. Capturar a exceção `sqlite3.IntegrityError` provocada pela restrição `CHECK`.
7. Consultar as tabelas `player`, `partida` e `performance` após o rollback.
8. Comparar os resultados obtidos com os esperados.

### Resultado esperado

- A performance inválida deve ser rejeitada pelo banco de dados.
- Deve ocorrer uma exceção `sqlite3.IntegrityError`.
- A partida inserida na mesma transação não deve permanecer registrada.
- O jogador previamente confirmado deve permanecer no banco.
- Contagens finais: 1 jogador, 0 partidas e 0 performances.

### Resultado obtido

- Exceção capturada: `CHECK constraint failed: headshots <= kills`.
- Jogadores encontrados: `1`.
- Partidas encontradas: `0`.
- Performances encontradas: `0`.
- Resultado apresentado no terminal: `RESULTADO: PASSOU`.

### Conclusão

**PASSOU.** A tentativa de registrar a performance inválida foi rejeitada e a transação foi desfeita. A partida não permaneceu no banco, enquanto o jogador previamente confirmado foi preservado.

### Evidência

Reexecução realizada em **21/10/2026, às 16:15:31**, por meio de script Python iniciado manualmente e com validações automatizadas dos resultados.

![Evidência de execução — QA-INT-001](docs/evidencias/QA-INT-001.png)

---

## QA-INT-002 — Registro de transação válida

**Tipo:** Teste de integração — cenário positivo

**Prioridade:** Alta

**Data:** 21/10/2026

**Status:** PASSOU

### Objetivo

Verificar se uma partida e uma performance válida são registradas na mesma transação, mantendo os relacionamentos corretos entre jogador, partida e performance.

### Pré-condições

- Banco SQLite de teste inicializado em memória.
- Jogador `jogador_teste` previamente cadastrado e confirmado com `commit()`.
- Funções `registrar_partida()` e `registrar_performance()` disponíveis.
- Conexão SQLite com chaves estrangeiras habilitadas.

### Procedimento

1. Inicializar o banco SQLite de teste em memória.
2. Cadastrar o jogador `jogador_teste` e confirmar seu registro.
3. Iniciar uma transação utilizando `with conn`.
4. Registrar uma partida válida no mapa Inferno (`de_inferno`), com vitória por 13×9.
5. Registrar uma performance associada à partida e ao jogador, com 20 kills, 15 deaths, 5 assists, 10 headshots e 22 rounds jogados.
6. Finalizar a transação sem exceções.
7. Consultar a quantidade de registros em `player`, `partida` e `performance`.
8. Executar uma consulta SQL com `JOIN` para validar os relacionamentos.
9. Consultar `conn.in_transaction` para verificar se há transação pendente.
10. Comparar os resultados obtidos com os esperados.

### Resultado esperado

- Partida e performance inseridas sem erros.
- IDs válidos retornados pelas funções.
- Exatamente 1 jogador, 1 partida e 1 performance.
- Relacionamento correto entre as três tabelas.
- Consulta SQL com `JOIN` retornando o jogador, o mapa e as estatísticas esperadas.
- Nenhuma transação pendente ao final da execução.

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

**PASSOU.** A partida e a performance foram registradas com sucesso. As consultas SQL confirmaram a presença dos registros e seu relacionamento no cenário testado. O bloco `with conn` terminou sem exceções e não havia transação pendente na conexão.

### Evidência

Reexecução realizada em **21/10/2026, às 16:34:38**, por meio de script Python iniciado manualmente, com verificações automatizadas por `assert`.

![Evidência de execução — QA-INT-002](docs/evidencias/QA-INT-002.png)

---

## Limitações dos testes

- Os cenários utilizaram SQLite em memória; não verificaram persistência após fechar e reabrir uma conexão com um banco em arquivo.
- Os dois casos validam comportamentos específicos de transação e integridade; não representam cobertura completa das funcionalidades do projeto.
- As capturas de tela registram reexecuções dos cenários originalmente exercitados no console Python.
- Os scripts usados nas reexecuções ainda não estão incluídos neste repositório.

## Resultado geral

**2 cenários executados — 2 aprovados — 0 falhas identificadas nos cenários testados.**

O projeto também possui uma suíte separada de testes automatizados com **Pytest**, executada pelo **GitHub Actions**. Esses testes automatizados não devem ser confundidos com os dois cenários de integração descritos neste documento.
