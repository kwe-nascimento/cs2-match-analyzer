"""Testes de integração do registro de performances com o schema real."""

import sqlite3

import pytest

from src.db import connect, init_db
from src.partidas import registrar_partida
from src.performances import registrar_performance


@pytest.fixture
def conn():
    c = connect()
    init_db(c)
    c.execute("INSERT INTO player (player_id, nickname) VALUES (1, 'eu')")
    registrar_partida(c, "2026-10-20", "de_mirage", "vitoria", 13, 7)
    c.commit()
    yield c
    c.close()


@pytest.fixture
def dados():
    return dict(
        player_id=1, partida_id=1,
        kills=20, deaths=12, assists=4, headshots=9, damage=2100,
        utility_damage=80, enemies_blinded=7, flash_assists=2,
        rounds_played=20, first_kills=3, first_deaths=2, kast_rounds=15,
    )


def test_registro_valido_preserva_todos_os_campos(conn, dados):
    performance_id = registrar_performance(conn, **dados)
    assert isinstance(performance_id, int)
    assert performance_id > 0
    assert conn.execute(
        "SELECT player_id, partida_id, kills, deaths, assists, headshots, damage, "
        "utility_damage, enemies_blinded, flash_assists, rounds_played, "
        "first_kills, first_deaths, kast_rounds "
        "FROM performance WHERE performance_id = ?", (performance_id,),
    ).fetchone() == tuple(dados.values())


def test_associacao_correta_e_ids_distintos(conn, dados):
    primeiro = registrar_performance(conn, **dados)
    conn.execute("INSERT INTO player (player_id, nickname) VALUES (2, 'colega')")
    partida_id = registrar_partida(conn, "2026-10-21", "de_inferno", "derrota", 7, 13)
    dados.update(player_id=2, partida_id=partida_id)
    segundo = registrar_performance(conn, **dados)
    assert primeiro != segundo
    assert conn.execute(
        "SELECT player.nickname, partida.mapa "
        "FROM performance "
        "JOIN player ON player.player_id = performance.player_id "
        "JOIN partida ON partida.partida_id = performance.partida_id "
        "WHERE performance.performance_id = ?", (segundo,),
    ).fetchone() == ("colega", "de_inferno")


@pytest.mark.parametrize("campo", [
    "kills", "deaths", "assists", "headshots", "damage", "utility_damage",
    "enemies_blinded", "flash_assists", "first_kills", "first_deaths", "kast_rounds",
])
def test_valores_negativos_rejeitados(conn, dados, campo):
    dados[campo] = -1
    with pytest.raises(sqlite3.IntegrityError):
        registrar_performance(conn, **dados)
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 0


@pytest.mark.parametrize("campo", [
    "player_id", "partida_id", "kills", "deaths", "assists", "headshots",
    "damage", "utility_damage", "enemies_blinded", "flash_assists",
    "rounds_played", "first_kills", "first_deaths", "kast_rounds",
])
def test_campos_obrigatorios_rejeitam_null(conn, dados, campo):
    dados[campo] = None
    with pytest.raises(sqlite3.IntegrityError):
        registrar_performance(conn, **dados)


@pytest.mark.parametrize("alteracoes", [
    {"headshots": 21}, {"first_kills": 21}, {"first_deaths": 13},
    {"first_kills": 11, "first_deaths": 10}, {"kast_rounds": 21},
    {"rounds_played": 0}, {"rounds_played": -1}, {"rounds_played": 19},
])
def test_regras_de_integridade_rejeitam_inconsistencias(conn, dados, alteracoes):
    dados.update(alteracoes)
    with pytest.raises(sqlite3.IntegrityError):
        registrar_performance(conn, **dados)


@pytest.mark.parametrize("campo", ["player_id", "partida_id"])
def test_ids_inexistentes_rejeitados(conn, dados, campo):
    dados[campo] = 999
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        registrar_performance(conn, **dados)


def test_performance_duplicada_rejeitada(conn, dados):
    registrar_performance(conn, **dados)
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        registrar_performance(conn, **dados)
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 1


@pytest.mark.parametrize("alteracoes", [
    dict(kills=0, deaths=0, assists=0, headshots=0, damage=0,
         utility_damage=0, enemies_blinded=0, flash_assists=0,
         first_kills=0, first_deaths=0, kast_rounds=0),
    dict(headshots=20, first_kills=20, first_deaths=0, kast_rounds=20),
    dict(first_kills=8, first_deaths=12, kast_rounds=20),
])
def test_valores_limite_validos(conn, dados, alteracoes):
    dados.update(alteracoes)
    registrar_performance(conn, **dados)
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 1


def test_mesmo_jogador_em_partidas_distintas_e_permitido(conn, dados):
    registrar_performance(conn, **dados)
    dados["partida_id"] = registrar_partida(
        conn, "2026-10-21", "de_inferno", "derrota", 7, 13
    )
    registrar_performance(conn, **dados)
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 2


def test_jogadores_distintos_na_mesma_partida_sao_permitidos(conn, dados):
    registrar_performance(conn, **dados)
    conn.execute("INSERT INTO player (player_id, nickname) VALUES (2, 'colega')")
    dados["player_id"] = 2
    registrar_performance(conn, **dados)
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 2


def test_rollback_desfaz_apenas_registro_pendente(conn, dados):
    registrar_performance(conn, **dados)
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM partida").fetchone()[0] == 1


def test_persistencia_apos_commit_e_reabertura(tmp_path, dados):
    caminho = str(tmp_path / "performances.sqlite")
    c = connect(caminho)
    try:
        init_db(c)
        c.execute("INSERT INTO player (player_id, nickname) VALUES (1, 'eu')")
        registrar_partida(c, "2026-10-20", "de_mirage", "vitoria", 13, 7)
        performance_id = registrar_performance(c, **dados)
        c.commit()
    finally:
        c.close()

    c = connect(caminho)
    try:
        assert c.execute(
            "SELECT player_id, partida_id, kills, deaths, assists, headshots, damage, "
            "utility_damage, enemies_blinded, flash_assists, rounds_played, "
            "first_kills, first_deaths, kast_rounds "
            "FROM performance WHERE performance_id = ?", (performance_id,),
        ).fetchone() == tuple(dados.values())
    finally:
        c.close()
