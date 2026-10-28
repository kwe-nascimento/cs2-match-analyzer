"""Consulta do histórico de partidas de um jogador."""

import sqlite3


def listar_partidas(conn: sqlite3.Connection, player_id: int) -> list[tuple]:
    """Retorna partidas da mais recente para a mais antiga, desempatando por ID.

    Cada tupla contém partida_id, data_partida, mapa, resultado, rounds_time,
    rounds_adversario, kills, deaths, assists e headshots, nessa ordem.
    Sem partidas associadas ao jogador, retorna uma lista vazia.
    Quem fornece a conexão controla transações e fechamento.
    """
    cursor = conn.execute(
        "SELECT partida.partida_id, partida.data_partida, partida.mapa, "
        "partida.resultado, partida.rounds_time, partida.rounds_adversario, "
        "performance.kills, performance.deaths, performance.assists, "
        "performance.headshots "
        "FROM partida "
        "JOIN performance ON performance.partida_id = partida.partida_id "
        "WHERE performance.player_id = ? "
        "ORDER BY partida.data_partida DESC, partida.partida_id DESC",
        (player_id,),
    )
    return cursor.fetchall()
