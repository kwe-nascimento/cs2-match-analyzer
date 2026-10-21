"""Testes de integração do registro de partidas com o schema real."""

import sqlite3

import pytest

from src.db import connect, init_db
from src.partidas import registrar_partida


@pytest.fixture
def conn():
    c = connect()
    init_db(c)
    yield c
    c.close()


@pytest.mark.parametrize(
    "resultado, rounds_time, rounds_adversario",
    [("vitoria", 13, 7), ("derrota", 7, 13), ("empate", 12, 12),
     ("vitoria", 13, 0), ("derrota", 0, 13)],
)
def test_registro_valido(conn, resultado, rounds_time, rounds_adversario):
    dados = ("2026-10-20", "de_mirage", resultado, rounds_time, rounds_adversario)
    partida_id = registrar_partida(conn, *dados)

    assert isinstance(partida_id, int)
    assert partida_id > 0
    assert conn.execute(
        "SELECT data_partida, mapa, resultado, rounds_time, rounds_adversario "
        "FROM partida WHERE partida_id = ?", (partida_id,),
    ).fetchone() == dados


@pytest.mark.parametrize(
    "resultado, rounds_time, rounds_adversario",
    [("vitoria", 7, 13), ("derrota", 13, 7), ("empate", 13, 7),
     ("vitoria", 12, 12), ("derrota", 12, 12)],
)
def test_resultado_incoerente(conn, resultado, rounds_time, rounds_adversario):
    with pytest.raises(sqlite3.IntegrityError):
        registrar_partida(conn, "2026-10-20", "de_mirage", resultado,
                          rounds_time, rounds_adversario)
    assert conn.execute("SELECT COUNT(*) FROM partida").fetchone()[0] == 0


@pytest.mark.parametrize(
    "campo, valor",
    [("data_partida", "20/10/2026"), ("data_partida", "2026-1-5"),
     ("data_partida", ""), ("mapa", ""), ("mapa", "   "),
     ("resultado", "ganhou"), ("rounds_time", -1),
     ("rounds_adversario", -1)]
    + [(campo, None) for campo in
       ("data_partida", "mapa", "resultado", "rounds_time", "rounds_adversario")],
)
def test_constraints_rejeitam_dados_invalidos(conn, campo, valor):
    dados = dict(data_partida="2026-10-20", mapa="de_mirage",
                 resultado="vitoria", rounds_time=13, rounds_adversario=7)
    dados[campo] = valor
    with pytest.raises(sqlite3.IntegrityError):
        registrar_partida(conn, **dados)
    assert conn.execute("SELECT COUNT(*) FROM partida").fetchone()[0] == 0


def test_ids_identificam_partidas_distintas(conn):
    primeiro = registrar_partida(conn, "2026-10-20", "de_mirage", "vitoria", 13, 7)
    segundo = registrar_partida(conn, "2026-10-21", "de_inferno", "derrota", 7, 13)
    assert primeiro != segundo
    assert conn.execute(
        "SELECT mapa FROM partida WHERE partida_id = ?", (segundo,),
    ).fetchone() == ("de_inferno",)


def test_mapa_com_texto_sql_e_armazenado_literalmente(conn):
    mapa = "de_mirage'); DROP TABLE partida; --"
    partida_id = registrar_partida(conn, "2026-10-20", mapa, "vitoria", 13, 7)
    assert conn.execute(
        "SELECT mapa FROM partida WHERE partida_id = ?", (partida_id,),
    ).fetchone() == (mapa,)


def test_dados_persistem_apos_commit_e_reabertura(tmp_path):
    caminho = str(tmp_path / "partidas.sqlite")
    dados = ("2026-10-20", "de_mirage", "vitoria", 13, 7)
    c = connect(caminho)
    try:
        init_db(c)
        partida_id = registrar_partida(c, *dados)
        c.commit()
    finally:
        c.close()

    c = connect(caminho)
    try:
        assert c.execute(
            "SELECT data_partida, mapa, resultado, rounds_time, rounds_adversario "
            "FROM partida WHERE partida_id = ?", (partida_id,),
        ).fetchone() == dados
    finally:
        c.close()


def test_chamador_pode_desfazer_registro(conn):
    registrar_partida(conn, "2026-10-20", "de_mirage", "vitoria", 13, 7)
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM partida").fetchone()[0] == 0
