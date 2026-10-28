"""Testes de integração do histórico com o schema real."""

import pytest

from src.consultas import listar_partidas
from src.db import connect, init_db
from src.registros import registrar_partida, registrar_performance


@pytest.fixture
def conn():
    c = connect()
    init_db(c)
    c.executemany(
        "INSERT INTO player (player_id, nickname) VALUES (?, ?)",
        [(1, "eu"), (2, "colega")],
    )
    yield c
    c.close()


def inserir_performance(conn, partida_id, player_id=1, kills=20):
    registrar_performance(
        conn, player_id=player_id, partida_id=partida_id,
        kills=kills, deaths=12, assists=4, headshots=9, damage=2100,
        utility_damage=80, enemies_blinded=7, flash_assists=2,
        rounds_played=20, first_kills=3, first_deaths=2, kast_rounds=15,
    )


@pytest.mark.parametrize(
    "resultado, rounds_time, rounds_adversario",
    [("vitoria", 13, 7), ("derrota", 7, 13), ("empate", 10, 10)],
)
def test_retorna_campos_da_partida_e_estatisticas(
    conn, resultado, rounds_time, rounds_adversario,
):
    partida_id = registrar_partida(
        conn, "2026-10-20", "de_mirage", resultado, rounds_time, rounds_adversario,
    )
    inserir_performance(conn, partida_id)

    assert listar_partidas(conn, 1) == [
        (partida_id, "2026-10-20", "de_mirage", resultado,
         rounds_time, rounds_adversario, 20, 12, 4, 9),
    ]


def test_multiplas_partidas_ordenadas_por_data_e_id_decrescentes(conn):
    ids = []
    # Datas fora da ordem de inserção e empate entre IDs não consecutivos.
    for data in ["2026-10-22", "2026-10-19", "2026-10-22", "2026-10-21"]:
        partida_id = registrar_partida(conn, data, "de_mirage", "vitoria", 13, 7)
        inserir_performance(conn, partida_id)
        ids.append(partida_id)

    partidas = listar_partidas(conn, 1)

    assert [partida[0] for partida in partidas] == [ids[2], ids[0], ids[3], ids[1]]


@pytest.mark.parametrize("player_id", [1, 999])
def test_sem_partidas_retorna_lista_vazia(conn, player_id):
    registrar_partida(conn, "2026-10-20", "de_mirage", "vitoria", 13, 7)

    assert listar_partidas(conn, player_id) == []


def test_isolamento_de_partidas_e_estatisticas_entre_jogadores(conn):
    compartilhada = registrar_partida(
        conn, "2026-10-20", "de_mirage", "vitoria", 13, 7,
    )
    exclusiva = registrar_partida(
        conn, "2026-10-21", "de_inferno", "derrota", 7, 13,
    )
    inserir_performance(conn, compartilhada, player_id=1, kills=20)
    inserir_performance(conn, compartilhada, player_id=2, kills=30)
    inserir_performance(conn, exclusiva, player_id=2, kills=25)

    assert listar_partidas(conn, 1) == [
        (compartilhada, "2026-10-20", "de_mirage", "vitoria", 13, 7, 20, 12, 4, 9),
    ]
    assert listar_partidas(conn, 2) == [
        (exclusiva, "2026-10-21", "de_inferno", "derrota", 7, 13, 25, 12, 4, 9),
        (compartilhada, "2026-10-20", "de_mirage", "vitoria", 13, 7, 30, 12, 4, 9),
    ]
    assert listar_partidas(conn, 999) == []


def test_player_id_com_texto_sql_nao_amplia_resultados(conn):
    partida_id = registrar_partida(conn, "2026-10-20", "de_mirage", "vitoria", 13, 7)
    inserir_performance(conn, partida_id)

    assert listar_partidas(conn, "1 OR 1=1") == []
    assert len(listar_partidas(conn, 1)) == 1
