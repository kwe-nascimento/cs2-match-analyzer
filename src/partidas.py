"""Registro de partidas com as regras de integridade do SQLite."""

import sqlite3


def registrar_partida(
    conn: sqlite3.Connection,
    data_partida: str,
    mapa: str,
    resultado: str,
    rounds_time: int,
    rounds_adversario: int,
) -> int:
    """Insere uma partida e retorna seu ID, sem confirmar a transação.

    A data deve seguir AAAA-MM-DD; o resultado deve ser 'vitoria',
    'derrota' ou 'empate', coerente com o placar. O schema valida os
    valores e os erros do SQLite são propagados para quem chamou.
    Quem fornece a conexão controla commit, rollback e fechamento.
    """
    cursor = conn.execute(
        "INSERT INTO partida "
        "(data_partida, mapa, resultado, rounds_time, rounds_adversario) "
        "VALUES (?, ?, ?, ?, ?)",
        (data_partida, mapa, resultado, rounds_time, rounds_adversario),
    )
    return cursor.lastrowid
