"""Estatísticas agregadas por mapa e classificação Best/Worst de um jogador."""

import sqlite3


def obter_estatisticas_mapas(
    conn: sqlite3.Connection, player_id: int,
) -> list[dict[str, str | int | float]]:
    """Retorna resumos ordenados por Win Rate, ADR e K/D decrescentes e nome crescente.

    Cada resumo contém mapa, partidas, vitorias, derrotas, empates, kd, kda,
    hs_percent, adr, kast_percent e win_rate. As razões usam os totais do mapa,
    sem arredondamento e sem mínimo de partidas. Amostras pequenas podem ser
    pouco representativas. Nomes são agrupados exatamente como armazenados;
    o desempate alfabético usa a ordem lexicográfica do Python, sensível a caixa.
    Retorna [] sem performances. Não altera registros ou controla a conexão
    e suas transações; commit, rollback e close ficam com o chamador.
    """
    dados = conn.execute(
        "SELECT partida.mapa, COUNT(*), "
        "SUM(CASE WHEN partida.resultado = 'vitoria' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN partida.resultado = 'derrota' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN partida.resultado = 'empate' THEN 1 ELSE 0 END), "
        "SUM(performance.kills), SUM(performance.deaths), "
        "SUM(performance.assists), SUM(performance.headshots), "
        "SUM(performance.damage), SUM(performance.rounds_played), "
        "SUM(performance.kast_rounds) "
        "FROM performance "
        "JOIN partida ON partida.partida_id = performance.partida_id "
        "WHERE performance.player_id = ? "
        "GROUP BY partida.mapa",
        (player_id,),
    ).fetchall()
    mapas = []
    for mapa, partidas, vitorias, derrotas, empates, kills, deaths, assists, headshots, damage, rounds, kast in dados:
        mapas.append({
            "mapa": mapa,
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
        })
    return sorted(mapas, key=lambda m: (-m["win_rate"], -m["adr"], -m["kd"], m["mapa"]))


def obter_melhor_mapa(
    conn: sqlite3.Connection, player_id: int,
) -> dict[str, str | int | float] | None:
    """Retorna o primeiro resumo da classificação, ou None sem performances."""
    mapas = obter_estatisticas_mapas(conn, player_id)
    return mapas[0] if mapas else None


def obter_pior_mapa(
    conn: sqlite3.Connection, player_id: int,
) -> dict[str, str | int | float] | None:
    """Retorna o último resumo da classificação, ou None sem performances.

    No empate total das métricas, o nome alfabeticamente maior fica por último.
    Com um único mapa, Best e Worst retornam o mesmo resumo.
    """
    mapas = obter_estatisticas_mapas(conn, player_id)
    return mapas[-1] if mapas else None
