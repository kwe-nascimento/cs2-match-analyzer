"""Regressões da manutenção de calendário, placar e instalação incremental."""
import sqlite3
from pathlib import Path

import pytest

from src.db import connect, init_db
from src.registros import registrar_partida, registrar_performance


@pytest.fixture
def conn():
    connection = connect()
    init_db(connection)
    yield connection
    connection.close()


def partida(conn, data="2026-10-29"):
    return registrar_partida(conn, data, "de_mirage", "vitoria", 13, 7)


def performance(conn, partida_id, nickname="jogador"):
    player_id = conn.execute(
        "INSERT INTO player (nickname) VALUES (?)", (nickname,)
    ).lastrowid
    return registrar_performance(
        conn, player_id=player_id, partida_id=partida_id,
        kills=20, deaths=12, assists=4, headshots=9, damage=2100,
        utility_damage=80, enemies_blinded=7, flash_assists=2,
        rounds_played=20, first_kills=3, first_deaths=2, kast_rounds=15,
    )


def snapshot(conn):
    return tuple(conn.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
                 for table in ("player", "partida", "performance"))


@pytest.mark.parametrize("data", [
    "2024-02-29", "2000-02-29", "1900-02-28", "2026-01-31", "0001-01-01",
])
def test_datas_reais(conn, data):
    pid = partida(conn, data)
    assert conn.execute("SELECT data_partida FROM partida WHERE partida_id=?", (pid,)).fetchone() == (data,)


@pytest.mark.parametrize("data", [
    "2026-02-29", "2026-02-30", "2026-04-31", "1900-02-29",
    "2026-13-01", "2026-00-15", "2026-01-00", "2026-99-99",
    "0000-01-01", "2026-2-9",
])
def test_datas_invalidas_insert(conn, data):
    partida(conn)
    before = snapshot(conn)
    with pytest.raises(sqlite3.IntegrityError):
        partida(conn, data)
    assert snapshot(conn) == before


@pytest.mark.parametrize("data", ["2026-02-29", "2026-04-31", "2026-13-01", "0000-01-01"])
def test_datas_invalidas_update(conn, data):
    pid = partida(conn)
    performance(conn, pid)
    before = snapshot(conn)
    with pytest.raises(sqlite3.IntegrityError, match="data_partida invalida"):
        conn.execute("UPDATE partida SET data_partida=? WHERE partida_id=?", (data, pid))
    assert snapshot(conn) == before


def test_data_valida_update(conn):
    pid = partida(conn)
    conn.execute("UPDATE partida SET data_partida=? WHERE partida_id=?", ("2024-02-29", pid))
    assert conn.execute("SELECT data_partida FROM partida WHERE partida_id=?", (pid,)).fetchone() == ("2024-02-29",)


@pytest.mark.parametrize("placar", [(14, 7), (13, 8), (15, 6)])
def test_placar_total_incompativel(conn, placar):
    pid = partida(conn)
    performance(conn, pid)
    before = snapshot(conn)
    with pytest.raises(sqlite3.IntegrityError, match="placar difere dos rounds_played registrados"):
        conn.execute("UPDATE partida SET rounds_time=?, rounds_adversario=? WHERE partida_id=?", (*placar, pid))
    assert snapshot(conn) == before


def test_placar_mesmo_total(conn):
    pid = partida(conn)
    performance(conn, pid)
    players, _, performances = snapshot(conn)
    conn.execute("UPDATE partida SET rounds_time=12, rounds_adversario=8 WHERE partida_id=?", (pid,))
    assert conn.execute("SELECT rounds_time, rounds_adversario FROM partida WHERE partida_id=?", (pid,)).fetchone() == (12, 8)
    assert snapshot(conn)[0] == players
    assert snapshot(conn)[2] == performances


def test_placar_sem_performance(conn):
    pid = partida(conn)
    conn.execute("UPDATE partida SET rounds_time=14 WHERE partida_id=?", (pid,))
    assert conn.execute("SELECT rounds_time, rounds_adversario FROM partida WHERE partida_id=?", (pid,)).fetchone() == (14, 7)


def test_resultado_incoerente(conn):
    pid = partida(conn)
    performance(conn, pid)
    before = snapshot(conn)
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        conn.execute("UPDATE partida SET rounds_time=7, rounds_adversario=13 WHERE partida_id=?", (pid,))
    assert snapshot(conn) == before


def test_placar_dois_jogadores(conn):
    pid = partida(conn)
    performance(conn, pid, "primeiro")
    performance(conn, pid, "segundo")
    before = snapshot(conn)
    with pytest.raises(sqlite3.IntegrityError, match="placar difere"):
        conn.execute("UPDATE partida SET rounds_adversario=8 WHERE partida_id=?", (pid,))
    assert snapshot(conn) == before
    conn.execute("UPDATE partida SET rounds_time=12, rounds_adversario=8 WHERE partida_id=?", (pid,))
    assert conn.execute("SELECT p.rounds_played, m.rounds_time + m.rounds_adversario FROM performance p JOIN partida m USING (partida_id)").fetchall() == [(20, 20), (20, 20)]
    assert snapshot(conn)[2] == before[2]


NEW_TRIGGERS = {"trg_partida_placar_update", "trg_partida_data_insert", "trg_partida_data_update"}


def triggers(conn):
    return conn.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' ORDER BY name").fetchall()


def test_init_repetida(conn):
    pid = partida(conn)
    performance(conn, pid)
    before, definitions = snapshot(conn), triggers(conn)
    init_db(conn)
    init_db(conn)
    assert triggers(conn) == definitions
    assert len(definitions) == 5
    assert NEW_TRIGGERS <= {name for name, _ in definitions}
    assert snapshot(conn) == before


def test_instalacao_banco_existente(tmp_path):
    path = str(tmp_path / "legado.sqlite")
    conn = connect(path)
    try:
        # Reconstrói o schema anterior sem os três triggers desta manutenção.
        schema = (Path(__file__).resolve().parents[1] / "sql/schema.sql").read_text(encoding="utf-8")
        conn.executescript(schema.split("-- Impede que o placar invalide")[0])
        assert not NEW_TRIGGERS & {name for name, _ in triggers(conn)}
        pid = partida(conn, "2026-02-30")
        performance(conn, pid)
        conn.execute("UPDATE partida SET rounds_time=14 WHERE partida_id=?", (pid,))
        conn.commit()
        before = snapshot(conn)
    finally:
        conn.close()
    conn = connect(path)
    try:
        init_db(conn)
        assert NEW_TRIGGERS <= {name for name, _ in triggers(conn)}
        assert snapshot(conn) == before  # Legado inválido não é corrigido.
        for sql, params in [
            ("UPDATE partida SET data_partida=? WHERE partida_id=?", ("2026-04-31", pid)),
            ("UPDATE partida SET rounds_time=15 WHERE partida_id=?", (pid,)),
        ]:
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(sql, params)
            assert snapshot(conn) == before
        with pytest.raises(sqlite3.IntegrityError):
            partida(conn, "1900-02-29")
        assert snapshot(conn) == before
    finally:
        conn.close()
