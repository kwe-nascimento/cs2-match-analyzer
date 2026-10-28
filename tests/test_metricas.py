"""Testes de integração das métricas com SQLite em memória."""

import pytest

from src.db import connect, init_db
from src.metricas import obter_metricas_partida, obter_resumo_jogador
from src.registros import registrar_partida, registrar_performance


@pytest.fixture
def conn():
    c = connect()
    init_db(c)
    c.executemany(
        "INSERT INTO player (player_id, nickname) VALUES (?, ?)",
        [(1, "eu"), (2, "colega"), (3, "sem_performance")],
    )
    c.commit()
    yield c
    c.close()


def inserir(conn, *, player_id=1, partida_id=None, placar=(13, 7),
            kills=20, deaths=12, assists=4, headshots=9, damage=2100, kast=15):
    if partida_id is None:
        time, adversario = placar
        resultado = "vitoria" if time > adversario else "derrota" if time < adversario else "empate"
        partida_id = registrar_partida(
            conn, "2026-10-28", "de_mirage", resultado, time, adversario,
        )
    registrar_performance(
        conn, player_id=player_id, partida_id=partida_id,
        kills=kills, deaths=deaths, assists=assists, headshots=headshots,
        damage=damage, utility_damage=0, enemies_blinded=0, flash_assists=0,
        rounds_played=sum(placar), first_kills=0, first_deaths=0,
        kast_rounds=kast,
    )
    return partida_id


def test_cinco_metricas_por_partida(conn):
    partida = inserir(conn)
    assert obter_metricas_partida(conn, 1, partida) == pytest.approx({
        "kd": 20 / 12, "kda": 24 / 12, "hs_percent": 45.0,
        "adr": 105.0, "kast_percent": 75.0,
    })


@pytest.mark.parametrize("resumo", [False, True])
def test_zero_mortes(conn, resumo):
    partida = inserir(conn, deaths=0)
    metricas = obter_resumo_jogador(conn, 1) if resumo else obter_metricas_partida(conn, 1, partida)
    assert metricas["kd"] == pytest.approx(20.0)
    assert metricas["kda"] == pytest.approx(24.0)


@pytest.mark.parametrize("resumo", [False, True])
def test_zero_kills(conn, resumo):
    partida = inserir(conn, kills=0, headshots=0)
    metricas = obter_resumo_jogador(conn, 1) if resumo else obter_metricas_partida(conn, 1, partida)
    assert metricas["hs_percent"] == pytest.approx(0.0)
    assert isinstance(metricas["hs_percent"], float)


@pytest.mark.parametrize("player_id, partida_id", [(1, 999), (999, 1), (2, 1)])
def test_performance_inexistente(conn, player_id, partida_id):
    inserir(conn)
    assert obter_metricas_partida(conn, player_id, partida_id) is None


def test_resumo_uma_partida(conn):
    inserir(conn)
    assert obter_resumo_jogador(conn, 1) == pytest.approx({
        "partidas": 1, "vitorias": 1, "derrotas": 0, "empates": 0,
        "kd": 20 / 12, "kda": 2.0, "hs_percent": 45.0,
        "adr": 105.0, "kast_percent": 75.0, "win_rate": 100.0,
    })


def test_resumo_multiplas_partidas_utiliza_totais(conn):
    inserir(conn, placar=(13, 0), kills=10, deaths=0, assists=2,
            headshots=1, damage=1000, kast=3)
    inserir(conn, placar=(7, 13), kills=30, deaths=10, assists=6,
            headshots=24, damage=2001, kast=17)
    inserir(conn, placar=(12, 12), kills=5, deaths=5, assists=1,
            headshots=0, damage=100, kast=1)
    # Totais: 45 kills, 15 deaths, 9 assists, 25 HS, 3101 damage, 57 rounds, 21 KAST.
    assert obter_resumo_jogador(conn, 1) == pytest.approx({
        "partidas": 3, "vitorias": 1, "derrotas": 1, "empates": 1,
        "kd": 3.0, "kda": 3.6, "hs_percent": 25 / 45 * 100,
        "adr": 3101 / 57, "kast_percent": 21 / 57 * 100,
        "win_rate": 100 / 3,
    })


@pytest.mark.parametrize("placar, win_rate", [((13, 7), 100.0), ((7, 13), 0.0), ((10, 10), 0.0)])
def test_win_rate_por_resultado(conn, placar, win_rate):
    inserir(conn, placar=placar)
    assert obter_resumo_jogador(conn, 1)["win_rate"] == pytest.approx(win_rate)


def test_isolamento_entre_jogadores_e_partidas(conn):
    compartilhada = inserir(conn)
    inserir(conn, player_id=2, partida_id=compartilhada, kills=40, deaths=2,
            assists=8, headshots=30, damage=4000, kast=20)
    exclusiva = inserir(conn, player_id=2)
    sem_performance = registrar_partida(conn, "2026-10-28", "de_inferno", "vitoria", 13, 7)
    assert obter_metricas_partida(conn, 1, exclusiva) is None
    assert obter_metricas_partida(conn, 1, sem_performance) is None
    assert obter_metricas_partida(conn, 2, compartilhada) == pytest.approx({
        "kd": 20.0, "kda": 24.0, "hs_percent": 75.0,
        "adr": 200.0, "kast_percent": 100.0,
    })
    assert obter_resumo_jogador(conn, 1)["partidas"] == 1
    assert obter_resumo_jogador(conn, 1)["kd"] == pytest.approx(20 / 12)
    assert obter_resumo_jogador(conn, 2) == pytest.approx({
        "partidas": 2, "vitorias": 2, "derrotas": 0, "empates": 0,
        "kd": 60 / 14, "kda": 72 / 14, "hs_percent": 65.0,
        "adr": 152.5, "kast_percent": 87.5, "win_rate": 100.0,
    })


@pytest.mark.parametrize("player_id", [3, 999])
def test_jogador_sem_performances(conn, player_id):
    inserir(conn)
    assert obter_resumo_jogador(conn, player_id) is None


@pytest.mark.parametrize("resumo", [False, True])
def test_percentuais_e_precisao_sem_arredondamento(conn, resumo):
    partida = inserir(conn, placar=(2, 1), kills=3, deaths=7, assists=2,
                      headshots=1, damage=10, kast=1)
    metricas = obter_resumo_jogador(conn, 1) if resumo else obter_metricas_partida(conn, 1, partida)
    for campo, esperado in {
        "kd": 3 / 7, "kda": 5 / 7, "hs_percent": 100 / 3,
        "adr": 10 / 3, "kast_percent": 100 / 3,
    }.items():
        assert metricas[campo] == pytest.approx(esperado, rel=1e-12, abs=1e-12)
    assert 0 <= metricas["hs_percent"] <= 100
    assert 0 <= metricas["kast_percent"] <= 100


@pytest.mark.parametrize("confirmar", [False, True])
def test_consultas_preservam_registros_e_transacao(conn, confirmar):
    partida = inserir(conn)
    if confirmar:
        conn.commit()
    antes = list(conn.iterdump())
    alteracoes = conn.total_changes
    transacao = conn.in_transaction

    obter_metricas_partida(conn, 1, partida)
    obter_resumo_jogador(conn, 1)
    obter_metricas_partida(conn, 999, partida)
    obter_resumo_jogador(conn, 999)

    assert list(conn.iterdump()) == antes
    assert conn.total_changes == alteracoes
    assert conn.in_transaction == transacao
    # A conexão continua aberta e o chamador ainda controla o rollback.
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == (1 if confirmar else 0)


@pytest.mark.parametrize("campo", ["player_id", "partida_id"])
def test_parametros_sql_tratados_como_valores(conn, campo):
    partida = inserir(conn)
    parametros = dict(player_id=1, partida_id=partida)
    parametros[campo] = "1 OR 1=1"
    assert obter_metricas_partida(conn, **parametros) is None
    assert obter_resumo_jogador(conn, "1 OR 1=1") is None
