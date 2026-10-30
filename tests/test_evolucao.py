"""Consultas e agregação com SQLite temporário, sem banco pessoal."""
from datetime import date

import pytest

from src.db import connect, init_db
from src.app_servicos import cadastrar_jogador, salvar_partida_completa
from src.evolucao import listar_evolucao, resumir_evolucao
from src.metricas import obter_metricas_partida


@pytest.fixture
def conn(tmp_path):
    c = connect(str(tmp_path / "evolucao.sqlite"))
    init_db(c)
    cadastrar_jogador(c, "eu")
    cadastrar_jogador(c, "colega")
    yield c
    c.close()


def inserir(c, dia=2, mapa="Mirage", player=1, kills=10, deaths=3,
            damage=1001, rounds=13, kast=4):
    return salvar_partida_completa(c, player, date(2026, 10, dia), mapa, rounds, 0,
        dict(kills=kills, deaths=deaths, assists=2, headshots=1, damage=damage,
             utility_damage=0, enemies_blinded=0, flash_assists=0,
             first_kills=0, first_deaths=0, kast_rounds=kast))


@pytest.mark.parametrize("player", [1, 999])
def test_vazio(conn, player):
    assert listar_evolucao(conn, player) == []
    assert resumir_evolucao([]) is None


def test_uma_partida_campos_precisao_e_definicoes_existentes(conn):
    partida = inserir(conn)
    r, = listar_evolucao(conn, 1)
    assert r == dict(partida_id=partida, data_partida="2026-10-02", mapa="de_mirage",
                    resultado="vitoria", kills=10, deaths=3, assists=2, headshots=1,
                    damage=1001, rounds_played=13, kast_rounds=4,
                    kd=10 / 3, adr=1001 / 13, kast_percent=4 / 13 * 100)
    existente = obter_metricas_partida(conn, 1, partida)
    assert {k: r[k] for k in ("kd", "adr", "kast_percent")} == {k: existente[k] for k in ("kd", "adr", "kast_percent")}


def test_multiplas_ordenacao_e_desempate(conn):
    a = inserir(conn, dia=3)
    b = inserir(conn, dia=1)
    c = inserir(conn, dia=1)
    assert [r["partida_id"] for r in listar_evolucao(conn, 1)] == [b, c, a]


@pytest.mark.parametrize("filtros,dias", [
    ({"mapa": "de_nuke"}, [3]),
    ({"data_inicial": "2026-10-02"}, [2, 3]),
    ({"data_final": "2026-10-02"}, [1, 2]),
    ({"data_inicial": date(2026, 10, 2), "data_final": date(2026, 10, 2)}, [2]),
    ({"mapa": "de_nuke", "data_inicial": "2026-10-03", "data_final": "2026-10-03"}, [3]),
    ({"mapa": "inexistente"}, []),
    ({"data_inicial": "2027-01-01"}, []),
    ({"data_inicial": "2026-10-03", "data_final": "2026-10-01"}, []),
])
def test_filtros(conn, filtros, dias):
    inserir(conn, dia=1)
    inserir(conn, dia=2)
    inserir(conn, dia=3, mapa="Nuke")
    assert [int(r["data_partida"][-2:]) for r in listar_evolucao(conn, 1, **filtros)] == dias


def test_zero_mortes_e_agregacao_pelos_totais(conn):
    inserir(conn, deaths=0, kills=10, rounds=13, damage=1000, kast=3)
    inserir(conn, deaths=10, kills=30, rounds=20, damage=2001, kast=17)
    registros = listar_evolucao(conn, 1)
    assert registros[0]["kd"] == 10
    assert resumir_evolucao(registros) == dict(partidas=2, kd=4, adr=3001 / 33, kast_percent=20 / 33 * 100)
    assert resumir_evolucao(registros)["kd"] != sum(r["kd"] for r in registros) / 2


def test_isolamento_inclusive_partida_compartilhada(conn):
    from src.registros import registrar_performance
    partida = inserir(conn)
    registrar_performance(conn, player_id=2, partida_id=partida, kills=1, deaths=0,
        assists=0, headshots=0, damage=1, utility_damage=0, enemies_blinded=0,
        flash_assists=0, rounds_played=13, first_kills=0, first_deaths=0, kast_rounds=1)
    conn.commit()
    inserir(conn, player=2, mapa="Nuke")
    assert len(listar_evolucao(conn, 1)) == 1
    assert len(listar_evolucao(conn, 2)) == 2
    assert listar_evolucao(conn, 2)[0]["kills"] == 1
    assert listar_evolucao(conn, 1, mapa="de_nuke") == []
    assert listar_evolucao(conn, 999) == []


@pytest.mark.parametrize("pendente", [False, True])
def test_consulta_preserva_banco_conexao_e_transacao(conn, pendente):
    inserir(conn)
    if pendente:
        conn.execute("INSERT INTO player (nickname) VALUES ('pendente')")
    antes = list(conn.iterdump()), conn.total_changes, conn.in_transaction
    listar_evolucao(conn, 1)
    listar_evolucao(conn, 999)
    assert (list(conn.iterdump()), conn.total_changes, conn.in_transaction) == antes
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM player").fetchone()[0] == 2


@pytest.mark.parametrize("campo", ["player_id", "mapa", "data_inicial", "data_final"])
def test_sql_parametrizado(conn, campo):
    inserir(conn)
    comandos = []
    conn.set_trace_callback(comandos.append)
    listar_evolucao(conn, **{**dict(player_id=1), campo: "' OR 1=1 --"})
    conn.set_trace_callback(None)
    assert len(comandos) == 1
    assert "''' OR 1=1 --'" in comandos[0]
    assert len(listar_evolucao(conn, 1)) == 1
