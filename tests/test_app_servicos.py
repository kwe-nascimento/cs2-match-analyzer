"""Serviços do MVP visual em bancos temporários, nunca no banco pessoal."""
from datetime import date
import sqlite3

import pytest

from src.app_servicos import (
    ROOT, abrir_banco, caminho_banco, cadastrar_jogador, listar_jogadores,
    normalizar_mapa, salvar_partida_completa, validar_formulario,
)
from src.consultas import listar_partidas
from src.metricas import obter_resumo_jogador


@pytest.fixture
def db_path(monkeypatch, tmp_path):
    path = tmp_path / "dados" / "teste.sqlite"
    monkeypatch.setenv("CS2_DB_PATH", str(path))
    return path


def stats(**changes):
    dados = dict(kills=20, deaths=10, assists=5, headshots=10, damage=2000,
                 utility_damage=80, enemies_blinded=3, flash_assists=1,
                 first_kills=2, first_deaths=1, kast_rounds=15)
    dados.update(changes)
    return dados


def salvar(conn, player_id, **changes):
    return salvar_partida_completa(conn, player_id, date(2026, 10, 29),
                                  "Mirage", 13, 7, stats(**changes))


def test_caminho_estavel(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("CS2_DB_PATH", raising=False)
    assert caminho_banco() == ROOT / "data/cs2.sqlite"
    monkeypatch.setenv("CS2_DB_PATH", "data/alternativo.sqlite")
    assert caminho_banco() == ROOT / "data/alternativo.sqlite"


def test_cadastro_persistencia_e_fechamento(db_path):
    with abrir_banco() as conn:
        pid = cadastrar_jogador(conn, "  jogador  ", "  ")
        assert listar_jogadores(conn) == [(pid, "jogador")]
        assert conn.execute("SELECT steam_id FROM player").fetchone() == (None,)
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
    with abrir_banco() as conn:
        assert listar_jogadores(conn) == [(pid, "jogador")]
        segundo = cadastrar_jogador(conn, "colega", " 12345 ")
        assert conn.execute("SELECT steam_id FROM player WHERE player_id=?", (segundo,)).fetchone() == ("12345",)
    assert db_path.exists()


@pytest.mark.parametrize("nickname", ["", "   "])
def test_nickname_vazio(db_path, nickname):
    with abrir_banco() as conn:
        with pytest.raises(ValueError, match="nickname"):
            cadastrar_jogador(conn, nickname)
        assert listar_jogadores(conn) == []


@pytest.mark.parametrize("nickname,steam", [("jogador", "outro"), ("outro", "123")])
def test_duplicidade(db_path, nickname, steam):
    with abrir_banco() as conn:
        cadastrar_jogador(conn, "jogador", "123")
        with pytest.raises(sqlite3.IntegrityError):
            cadastrar_jogador(conn, nickname, steam)
        assert len(listar_jogadores(conn)) == 1
        assert not conn.in_transaction


@pytest.mark.parametrize("entrada,esperado", [
    ("Mirage", "de_mirage"), (" mirage ", "de_mirage"),
    ("de_mirage", "de_mirage"), ("DE MIRAGE", "de_mirage"),
    ("aim_custom", "aim_custom"), ("cs_office", "cs_office"),
])
def test_mapas_canonicos(entrada, esperado):
    assert normalizar_mapa(entrada) == esperado


def test_mapa_vazio():
    with pytest.raises(ValueError, match="mapa"):
        normalizar_mapa(" ")


@pytest.mark.parametrize("placar,resultado", [((13, 7), "vitoria"), ((7, 13), "derrota"), ((10, 10), "empate")])
def test_partida_completa_persistencia(db_path, placar, resultado):
    with abrir_banco() as conn:
        pid = cadastrar_jogador(conn, "eu")
        partida = salvar_partida_completa(conn, pid, date(2026, 10, 29), "Mirage", *placar, stats())
        assert not conn.in_transaction
    with abrir_banco() as conn:
        assert conn.execute("SELECT resultado, mapa FROM partida WHERE partida_id=?", (partida,)).fetchone() == (resultado, "de_mirage")
        assert conn.execute("SELECT rounds_played FROM performance").fetchone() == (sum(placar),)
        assert listar_partidas(conn, pid)[0][0] == partida
        assert obter_resumo_jogador(conn, pid)["partidas"] == 1


@pytest.mark.parametrize("changes", [{"headshots": 21}, {"kast_rounds": 21}, {"kills": -1}])
def test_rollback_performance_invalida(db_path, changes):
    with abrir_banco() as conn:
        pid = cadastrar_jogador(conn, "eu")
        with pytest.raises(sqlite3.IntegrityError):
            salvar(conn, pid, **changes)
        assert conn.execute("SELECT COUNT(*) FROM partida").fetchone() == (0,)
        assert conn.execute("SELECT COUNT(*) FROM performance").fetchone() == (0,)
        assert listar_jogadores(conn) == [(pid, "eu")]
        assert not conn.in_transaction


def test_isolamento_e_sql_parametrizado(db_path):
    with abrir_banco() as conn:
        pid = cadastrar_jogador(conn, "eu'); DROP TABLE player; --")
        colega = cadastrar_jogador(conn, "colega")
        salvar(conn, pid)
        assert len(listar_partidas(conn, pid)) == 1
        assert listar_partidas(conn, colega) == []
        assert obter_resumo_jogador(conn, colega) is None
        with pytest.raises(sqlite3.IntegrityError):
            salvar(conn, "1 OR 1=1")
        assert conn.execute("SELECT COUNT(*) FROM partida").fetchone() == (1,)


@pytest.mark.parametrize("changes,rounds_time,rounds_adversario,data,mapa,mensagem", [
    ({"kills": -1}, 13, 7, date(2026, 1, 1), "Mirage", "negativos"),
    ({}, 0, 0, date(2026, 1, 1), "Mirage", "maior que zero"),
    ({"headshots": 21}, 13, 7, date(2026, 1, 1), "Mirage", "Headshots"),
    ({"first_kills": 21}, 13, 7, date(2026, 1, 1), "Mirage", "First Kills"),
    ({"first_deaths": 11}, 13, 7, date(2026, 1, 1), "Mirage", "First Deaths"),
    ({"first_kills": 15, "first_deaths": 6}, 13, 7, date(2026, 1, 1), "Mirage", "First Kills + First Deaths"),
    ({"kast_rounds": 21}, 13, 7, date(2026, 1, 1), "Mirage", "KAST Rounds"),
    ({}, 13, 7, None, "Mirage", "data válida"),
    ({}, 13, 7, date(2026, 1, 1), " ", "mapa"),
])
def test_validacao_amigavel(changes, rounds_time, rounds_adversario, data, mapa, mensagem):
    erros = validar_formulario(data, mapa, rounds_time, rounds_adversario, stats(**changes))
    assert any(mensagem in erro for erro in erros)


def test_validacao_correta():
    assert validar_formulario(date(2026, 1, 1), "Mirage", 13, 7, stats()) == []


def test_nao_confirma_transacao_alheia(db_path):
    with abrir_banco() as conn:
        pid = cadastrar_jogador(conn, "eu")
        conn.execute("INSERT INTO player (nickname) VALUES ('pendente')")
        with pytest.raises(ValueError, match="transação anterior"):
            salvar(conn, pid)
        assert conn.in_transaction
        conn.rollback()
        assert listar_jogadores(conn) == [(pid, "eu")]


def test_fecha_conexao_em_erro(db_path):
    with pytest.raises(RuntimeError):
        with abrir_banco() as conn:
            raise RuntimeError("teste")
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
