"""Evolução cronológica e razões dos totais, sem efeitos na conexão."""

from datetime import date
import sqlite3


def _metricas(kills, deaths, damage, rounds_played, kast_rounds):
    return {
        "kd": kills / max(1, deaths),
        "adr": damage / rounds_played,
        "kast_percent": kast_rounds / rounds_played * 100,
    }


def listar_evolucao(
    conn: sqlite3.Connection, player_id: int, mapa: str | None = None,
    data_inicial: str | date | None = None,
    data_final: str | date | None = None,
) -> list[dict]:
    """Retorna dados brutos e kd/adr/kast_percent por partida, sem arredondar.

    Datas são date ou strings ISO YYYY-MM-DD; limites inclusivos. Mapa é
    comparado exatamente como armazenado. None omite um filtro. Intervalo
    invertido retorna []. Ordem: data_partida ASC, partida_id ASC.
    Não grava, confirma, reverte ou fecha a conexão fornecida pelo chamador.
    """
    filtros = ["performance.player_id = ?"]
    parametros = [player_id]
    for coluna, operador, valor in [
        ("partida.mapa", "=", mapa),
        ("partida.data_partida", ">=", data_inicial),
        ("partida.data_partida", "<=", data_final),
    ]:
        if valor is not None:
            filtros.append(f"{coluna} {operador} ?")
            parametros.append(valor.isoformat() if isinstance(valor, date) else valor)
    campos = (
        "partida_id", "data_partida", "mapa", "resultado", "kills", "deaths",
        "assists", "headshots", "damage", "rounds_played", "kast_rounds",
    )
    dados = conn.execute(
        "SELECT partida.partida_id, partida.data_partida, partida.mapa, "
        "partida.resultado, performance.kills, performance.deaths, "
        "performance.assists, performance.headshots, performance.damage, "
        "performance.rounds_played, performance.kast_rounds "
        "FROM partida JOIN performance ON performance.partida_id = partida.partida_id "
        "WHERE " + " AND ".join(filtros) +
        " ORDER BY partida.data_partida ASC, partida.partida_id ASC",
        parametros,
    ).fetchall()
    registros = []
    for valores in dados:
        registro = dict(zip(campos, valores))
        registro.update(_metricas(*(registro[c] for c in
                                   ("kills", "deaths", "damage", "rounds_played", "kast_rounds"))))
        registros.append(registro)
    return registros


def resumir_evolucao(registros: list[dict]) -> dict | None:
    """Agrega os registros filtrados pelos totais; None para lista vazia."""
    if not registros:
        return None
    totais = [sum(r[c] for r in registros) for c in
              ("kills", "deaths", "damage", "rounds_played", "kast_rounds")]
    return {"partidas": len(registros), **_metricas(*totais)}
