"""Integração das análises por mapa com SQLite em memória."""

import pytest

from src.db import connect, init_db
from src.mapas import obter_estatisticas_mapas, obter_melhor_mapa, obter_pior_mapa
from src.metricas import obter_resumo_jogador
from src.registros import registrar_partida, registrar_performance


@pytest.fixture
def conn():
    c = connect()
    init_db(c)
    c.executemany("INSERT INTO player (player_id, nickname) VALUES (?, ?)",
                  [(1, "eu"), (2, "colega"), (3, "sem_performance")])
    c.commit()
    yield c
    c.close()


def inserir(conn, *, mapa="de_mirage", player_id=1, partida_id=None,
            placar=(13, 7), kills=20, deaths=12, assists=4,
            headshots=9, damage=2100, kast=15):
    if partida_id is None:
        time, adversario = placar
        resultado = "vitoria" if time > adversario else "derrota" if time < adversario else "empate"
        partida_id = registrar_partida(conn, "2026-10-29", mapa, resultado, time, adversario)
    registrar_performance(
        conn, player_id=player_id, partida_id=partida_id,
        kills=kills, deaths=deaths, assists=assists, headshots=headshots,
        damage=damage, utility_damage=0, enemies_blinded=0, flash_assists=0,
        rounds_played=sum(placar), first_kills=0, first_deaths=0, kast_rounds=kast,
    )
    return partida_id


def test_um_mapa_uma_partida(conn):
    inserir(conn)
    mapas = obter_estatisticas_mapas(conn, 1)
    assert len(mapas) == 1
    resumo = mapas[0]
    assert resumo["mapa"] == "de_mirage"
    assert {k: v for k, v in resumo.items() if k != "mapa"} == pytest.approx({
        "partidas": 1, "vitorias": 1, "derrotas": 0, "empates": 0,
        "kd": 20 / 12, "kda": 2.0, "hs_percent": 45.0,
        "adr": 105.0, "kast_percent": 75.0, "win_rate": 100.0,
    })
    assert obter_melhor_mapa(conn, 1) == resumo == obter_pior_mapa(conn, 1)


def test_agregacao_pelos_totais_e_resultados(conn):
    inserir(conn, placar=(13, 0), kills=10, deaths=0, assists=2,
            headshots=1, damage=1000, kast=3)
    inserir(conn, placar=(7, 13), kills=30, deaths=10, assists=6,
            headshots=24, damage=2001, kast=17)
    inserir(conn, placar=(12, 12), kills=5, deaths=5, assists=1,
            headshots=0, damage=100, kast=1)
    resumo = obter_estatisticas_mapas(conn, 1)[0]
    assert {k: v for k, v in resumo.items() if k != "mapa"} == pytest.approx({
        "partidas": 3, "vitorias": 1, "derrotas": 1, "empates": 1,
        "kd": 45 / 15, "kda": 54 / 15, "hs_percent": 25 / 45 * 100,
        "adr": 3101 / 57, "kast_percent": 21 / 57 * 100, "win_rate": 1 / 3 * 100,
    })
    assert {k: v for k, v in resumo.items() if k != "mapa"} == obter_resumo_jogador(conn, 1)
    assert resumo["kd"] != pytest.approx((10 + 3 + 1) / 3)
    assert resumo["adr"] != pytest.approx((1000 / 13 + 2001 / 20 + 100 / 24) / 3)


@pytest.mark.parametrize("placar,contagens", [
    ((13, 7), (1, 0, 0, 100.0)), ((7, 13), (0, 1, 0, 0.0)),
    ((10, 10), (0, 0, 1, 0.0)),
])
def test_resultados(conn, placar, contagens):
    inserir(conn, placar=placar)
    resumo = obter_estatisticas_mapas(conn, 1)[0]
    assert tuple(resumo[k] for k in ["vitorias", "derrotas", "empates", "win_rate"]) == contagens


@pytest.mark.parametrize("criterio", ["win_rate", "adr", "kd", "mapa"])
@pytest.mark.parametrize("inverter", [False, True])
def test_classificacao_e_desempates(conn, criterio, inverter):
    # Os critérios inferiores favorecem zulu quando o superior favorece alfa.
    alfa = dict(mapa="de_alfa", kills=10, deaths=10, damage=1000)
    zulu = dict(mapa="de_zulu", kills=10, deaths=10, damage=1000)
    if criterio == "win_rate":
        zulu.update(placar=(7, 13), kills=50, damage=5000)
    elif criterio == "adr":
        alfa.update(damage=2000)
        zulu.update(kills=50)
    elif criterio == "kd":
        alfa.update(kills=30)
    for valores in ([zulu, alfa] if inverter else [alfa, zulu]):
        inserir(conn, **valores)
    mapas = obter_estatisticas_mapas(conn, 1)
    assert [m["mapa"] for m in mapas] == ["de_alfa", "de_zulu"]
    assert obter_melhor_mapa(conn, 1) == mapas[0]
    assert obter_pior_mapa(conn, 1) == mapas[-1]


def test_multiplos_mapas_nao_misturam_totais(conn):
    inserir(conn, mapa="de_nuke", placar=(7, 13))
    inserir(conn, mapa="de_mirage", kills=10)
    inserir(conn, mapa="de_mirage", kills=30)
    inserir(conn, mapa="de_inferno", placar=(10, 10), damage=4000)
    mapas = obter_estatisticas_mapas(conn, 1)
    assert [m["mapa"] for m in mapas] == ["de_mirage", "de_inferno", "de_nuke"]
    assert [m["partidas"] for m in mapas] == [2, 1, 1]
    assert [m["kd"] for m in mapas] == pytest.approx([40 / 24, 20 / 12, 20 / 12])


@pytest.mark.parametrize("player_id", [1, 3, 999])
def test_sem_partidas(conn, player_id):
    inserir(conn, player_id=2)
    registrar_partida(conn, "2026-10-29", "de_nuke", "vitoria", 13, 7)
    assert obter_estatisticas_mapas(conn, player_id) == []
    assert obter_melhor_mapa(conn, player_id) is None
    assert obter_pior_mapa(conn, player_id) is None


def test_isolamento_e_partidas_sem_performance(conn):
    compartilhada = inserir(conn)
    inserir(conn, player_id=2, partida_id=compartilhada, kills=40,
            deaths=2, damage=4000)
    inserir(conn, player_id=2, mapa="de_nuke", placar=(7, 13))
    registrar_partida(conn, "2026-10-29", "de_inferno", "vitoria", 13, 7)
    primeiro = obter_estatisticas_mapas(conn, 1)
    segundo = obter_estatisticas_mapas(conn, 2)
    assert len(primeiro) == 1
    assert primeiro[0]["partidas"] == 1
    assert primeiro[0]["kd"] == pytest.approx(20 / 12)
    assert [m["mapa"] for m in segundo] == ["de_mirage", "de_nuke"]
    assert segundo[0]["kd"] == 20.0
    assert segundo[0]["adr"] == 200.0


@pytest.mark.parametrize("kills,deaths,headshots", [(0, 12, 0), (20, 0, 9), (0, 0, 0)])
def test_zeros(conn, kills, deaths, headshots):
    inserir(conn, kills=kills, deaths=deaths, headshots=headshots)
    resumo = obter_estatisticas_mapas(conn, 1)[0]
    assert resumo["kd"] == kills / max(1, deaths)
    assert resumo["kda"] == (kills + 4) / max(1, deaths)
    assert resumo["hs_percent"] == (headshots / kills * 100 if kills else 0.0)
    assert isinstance(resumo["hs_percent"], float)


def test_precisao_sem_arredondamento(conn):
    inserir(conn, placar=(2, 1), kills=3, deaths=7, assists=2,
            headshots=1, damage=10, kast=1)
    resumo = obter_estatisticas_mapas(conn, 1)[0]
    for campo, valor in {"kd": 3 / 7, "kda": 5 / 7, "hs_percent": 1 / 3 * 100,
                         "adr": 10 / 3, "kast_percent": 1 / 3 * 100}.items():
        assert resumo[campo] == valor
        assert resumo[campo] != round(valor, 2)


@pytest.mark.parametrize("confirmar", [False, True])
def test_preservacao_registros_e_transacao(conn, confirmar):
    inserir(conn)
    if confirmar:
        conn.commit()
    antes, alteracoes, transacao = list(conn.iterdump()), conn.total_changes, conn.in_transaction
    for consulta in [obter_estatisticas_mapas, obter_melhor_mapa, obter_pior_mapa]:
        consulta(conn, 1)
        consulta(conn, 999)
        assert conn.in_transaction == transacao
        assert conn.total_changes == alteracoes
        assert list(conn.iterdump()) == antes
    conn.rollback()
    assert conn.execute("SELECT COUNT(*) FROM performance").fetchone()[0] == (1 if confirmar else 0)


@pytest.mark.parametrize("payload", ["1 OR 1=1", "1; DROP TABLE performance; --", "' OR '1'='1"])
def test_sql_injection_player_id(conn, payload):
    inserir(conn)
    antes = list(conn.iterdump())
    assert obter_estatisticas_mapas(conn, payload) == []
    assert obter_melhor_mapa(conn, payload) is None
    assert obter_pior_mapa(conn, payload) is None
    assert list(conn.iterdump()) == antes


def test_nome_mapa_sql_literal(conn):
    nome = "de_mirage'; DROP TABLE partida; --"
    inserir(conn, mapa=nome)
    assert obter_estatisticas_mapas(conn, 1)[0]["mapa"] == nome
    assert conn.execute("SELECT COUNT(*) FROM partida").fetchone() == (1,)
