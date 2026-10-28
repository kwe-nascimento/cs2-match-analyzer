"""Métricas por partida e resumo acumulado de um jogador."""

import sqlite3


def obter_metricas_partida(
    conn: sqlite3.Connection, player_id: int, partida_id: int,
) -> dict[str, float] | None:
    """Retorna as cinco métricas sem arredondar, ou None sem performance."""
    dados = conn.execute(
        "SELECT kills, deaths, assists, headshots, damage, rounds_played, "
        "kast_rounds FROM performance WHERE player_id = ? AND partida_id = ?",
        (player_id, partida_id),
    ).fetchone()
    if dados is None:
        return None

    kills, deaths, assists, headshots, damage, rounds, kast = dados
    return {
        "kd": kills / max(1, deaths),
        "kda": (kills + assists) / max(1, deaths),
        "hs_percent": headshots / kills * 100 if kills else 0.0,
        "adr": damage / rounds,
        "kast_percent": kast / rounds * 100,
    }


def obter_resumo_jogador(
    conn: sqlite3.Connection, player_id: int,
) -> dict[str, int | float] | None:
    """Calcula razões pelos totais; retorna None sem partidas associadas.

    Consultas não alteram registros. Transações e fechamento da conexão
    permanecem sob responsabilidade de quem chamou as funções.
    """
    dados = conn.execute(
        "SELECT COUNT(*), "
        "SUM(CASE WHEN partida.resultado = 'vitoria' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN partida.resultado = 'derrota' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN partida.resultado = 'empate' THEN 1 ELSE 0 END), "
        "SUM(performance.kills), SUM(performance.deaths), "
        "SUM(performance.assists), SUM(performance.headshots), "
        "SUM(performance.damage), SUM(performance.rounds_played), "
        "SUM(performance.kast_rounds) "
        "FROM performance "
        "JOIN partida ON partida.partida_id = performance.partida_id "
        "WHERE performance.player_id = ?",
        (player_id,),
    ).fetchone()
    partidas, vitorias, derrotas, empates, kills, deaths, assists, headshots, damage, rounds, kast = dados
    if partidas == 0:
        return None

    return {
        "partidas": partidas,
        "vitorias": vitorias,
        "derrotas": derrotas,
        "empates": empates,
        "kd": kills / max(1, deaths),
        "kda": (kills + assists) / max(1, deaths),
        "hs_percent": headshots / kills * 100 if kills else 0.0,
        "adr": damage / rounds,
        "kast_percent": kast / rounds * 100,
        "win_rate": vitorias / partidas * 100,
    }
