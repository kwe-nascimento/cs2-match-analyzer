"""Registro de partidas e performances com as regras de integridade do SQLite."""

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


def registrar_performance(
    conn: sqlite3.Connection,
    *,
    player_id: int,
    partida_id: int,
    kills: int,
    deaths: int,
    assists: int,
    headshots: int,
    damage: int,
    utility_damage: int,
    enemies_blinded: int,
    flash_assists: int,
    rounds_played: int,
    first_kills: int,
    first_deaths: int,
    kast_rounds: int,
) -> int:
    """Insere uma performance e retorna seu ID, sem confirmar a transação.

    Os IDs devem identificar jogador e partida existentes. Os demais
    parâmetros correspondem às colunas de dados brutos do schema.
    O SQLite valida os valores, os relacionamentos e a duplicidade;
    suas exceções são propagadas. Quem fornece a conexão controla
    commit, rollback e fechamento.
    """
    cursor = conn.execute(
        "INSERT INTO performance ("
        "player_id, partida_id, kills, deaths, assists, headshots, damage, "
        "utility_damage, enemies_blinded, flash_assists, rounds_played, "
        "first_kills, first_deaths, kast_rounds"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (player_id, partida_id, kills, deaths, assists, headshots, damage,
         utility_damage, enemies_blinded, flash_assists, rounds_played,
         first_kills, first_deaths, kast_rounds),
    )
    return cursor.lastrowid
