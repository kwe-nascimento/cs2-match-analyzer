"""Testes das regras de qualidade de dados do schema (MVP 1)."""
import sqlite3

import pytest

from src.db import connect, init_db


@pytest.fixture
def conn():
    c = connect(":memory:")
    init_db(c)
    c.execute("INSERT INTO player (player_id, nickname) VALUES (1, 'eu')")
    c.execute(
        "INSERT INTO partida (partida_id, data_partida, mapa, resultado, rounds_time, rounds_adversario) "
        "VALUES (1, '2026-10-20', 'de_mirage', 'vitoria', 13, 7)"
    )
    yield c
    c.close()


def perf(**overrides):
    """Performance valida (partida 1 = 13x7 = 20 rounds). Sobrescreva so o que quer quebrar."""
    base = dict(
        player_id=1, partida_id=1,
        kills=20, deaths=12, assists=4, headshots=9, damage=2100,
        utility_damage=80, enemies_blinded=7, flash_assists=2,
        rounds_played=20, first_kills=3, first_deaths=2, kast_rounds=15,
    )
    base.update(overrides)
    return base


def insert_perf(conn, data):
    cols = ", ".join(data)
    marks = ", ".join(f":{k}" for k in data)
    conn.execute(f"INSERT INTO performance ({cols}) VALUES ({marks})", data)


# ---------- caminho feliz ----------

def test_performance_valida_e_aceita(conn):
    insert_perf(conn, perf())
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == 1


def test_valores_limite_validos(conn):
    # tudo zerado possivel, headshots == kills, kast == rounds
    insert_perf(conn, perf(kills=0, headshots=0, first_kills=0, assists=0,
                           kast_rounds=20, first_deaths=0, deaths=0))
    insert_ok = conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0]
    assert insert_ok == 1


def test_headshots_igual_a_kills_e_valido(conn):
    insert_perf(conn, perf(kills=10, headshots=10, first_kills=0))


# ---------- regras de qualidade: dados invalidos devem ser rejeitados ----------

@pytest.mark.parametrize(
    "campo, valor",
    [
        ("kills", -1), ("deaths", -1), ("assists", -1), ("headshots", -1),
        ("damage", -1), ("utility_damage", -1), ("enemies_blinded", -1),
        ("flash_assists", -1), ("first_kills", -1), ("first_deaths", -1),
        ("kast_rounds", -1),
    ],
    ids=lambda v: str(v),
)
def test_valores_negativos_sao_rejeitados(conn, campo, valor):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(**{campo: valor}))


def test_headshots_maior_que_kills_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(kills=5, headshots=6, first_kills=0))


def test_kast_maior_que_rounds_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(kast_rounds=21))


def test_first_kill_mais_first_death_maior_que_rounds_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(first_kills=11, first_deaths=10, kills=20, deaths=12))


def test_first_kills_maior_que_kills_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(kills=2, headshots=1, first_kills=3))


def test_first_deaths_maior_que_deaths_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(deaths=1, first_deaths=2))


def test_rounds_played_zero_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(rounds_played=0, first_kills=0, first_deaths=0, kast_rounds=0))


def test_rounds_played_diferente_do_placar_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(rounds_played=19))


def test_update_de_rounds_played_fora_do_placar_e_rejeitado(conn):
    insert_perf(conn, perf())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE performance SET rounds_played = 25 WHERE performance_id = 1")


# ---------- relacionamentos ----------

def test_performance_duplicada_para_mesma_partida_e_rejeitada(conn):
    insert_perf(conn, perf())
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf())


def test_performance_com_player_inexistente_e_rejeitada(conn):
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(player_id=999))


def test_performance_com_partida_inexistente_e_rejeitada(conn):
    # a trigger de placar nao acha a partida; a FK tambem deve barrar
    with pytest.raises(sqlite3.IntegrityError):
        insert_perf(conn, perf(partida_id=999))


def test_nickname_duplicado_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO player (nickname) VALUES ('eu')")


# ---------- partida ----------

@pytest.mark.parametrize(
    "resultado, time, adv",
    [("vitoria", 7, 13), ("derrota", 13, 7), ("empate", 13, 7), ("vitoria", 10, 10)],
    ids=["vitoria-com-placar-de-derrota", "derrota-com-placar-de-vitoria",
         "empate-com-placar-desigual", "vitoria-com-placar-empatado"],
)
def test_resultado_incoerente_com_placar_e_rejeitado(conn, resultado, time, adv):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO partida (data_partida, mapa, resultado, rounds_time, rounds_adversario) "
            "VALUES ('2026-10-20', 'de_inferno', ?, ?, ?)", (resultado, time, adv),
        )


def test_resultado_fora_do_dominio_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO partida (data_partida, mapa, resultado, rounds_time, rounds_adversario) "
            "VALUES ('2026-10-20', 'de_inferno', 'ganhou', 13, 7)"
        )


@pytest.mark.parametrize("data", ["20/10/2026", "2026-1-5", "ontem", ""])
def test_data_em_formato_invalido_e_rejeitada(conn, data):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO partida (data_partida, mapa, resultado, rounds_time, rounds_adversario) "
            "VALUES (?, 'de_inferno', 'vitoria', 13, 7)", (data,),
        )


def test_mapa_vazio_e_rejeitado(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO partida (data_partida, mapa, resultado, rounds_time, rounds_adversario) "
            "VALUES ('2026-10-20', '   ', 'vitoria', 13, 7)"
        )
