"""Fluxos reais de formulário e rerun com Streamlit AppTest."""
from pathlib import Path
from datetime import date

import pytest
from streamlit.testing.v1 import AppTest

from src.app_servicos import abrir_banco, cadastrar_jogador, salvar_partida_completa

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def app_env(monkeypatch, tmp_path):
    path = tmp_path / "ui.sqlite"
    monkeypatch.setenv("CS2_DB_PATH", str(path))
    return path


def iniciar():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    return app


def botao(app, label):
    return next(b for b in app.button if b.label == label)


def texto(app, label):
    return next(t for t in app.text_input if t.label == label)


def numero(app, label):
    return next(n for n in app.number_input if n.label == label)


def cadastrar(app, nome):
    texto(app, "Nickname").set_value(nome)
    botao(app, "Cadastrar jogador").click().run()
    assert not app.exception


def dados(conn):
    return tuple(conn.execute(f"SELECT * FROM {t} ORDER BY 1").fetchall() for t in ["player", "partida", "performance"])


def test_carregamento_sem_insercao_e_primeiro_cadastro(app_env):
    app = iniciar()
    assert any("Cadastre" in i.value or "cadastre" in i.value for i in app.info)
    with abrir_banco() as conn:
        assert dados(conn) == ([], [], [])
    app.run()
    cadastrar(app, "jogador")
    assert app.selectbox(key="jogador").value == 1
    assert any("ainda não tem partidas" in i.value for i in app.info)
    with abrir_banco() as conn:
        antes = dados(conn)
    app.run()
    with abrir_banco() as conn:
        assert dados(conn) == antes


@pytest.mark.parametrize("nome", ["", "   "])
def test_erro_cadastro_sem_traceback(app_env, nome):
    app = iniciar()
    texto(app, "Nickname").set_value(nome)
    botao(app, "Cadastrar jogador").click().run()
    assert not app.exception
    assert any("nickname" in e.value for e in app.error)
    with abrir_banco() as conn:
        assert conn.execute("SELECT COUNT(*) FROM player").fetchone() == (0,)


def test_cadastro_duplicado_sem_traceback(app_env):
    app = iniciar()
    cadastrar(app, "eu")
    cadastrar(app, "eu")
    assert any("já cadastrado" in e.value for e in app.error)
    with abrir_banco() as conn:
        assert conn.execute("SELECT COUNT(*) FROM player").fetchone() == (1,)


def test_registro_dashboard_historico_e_reruns(app_env):
    app = iniciar()
    cadastrar(app, "eu")
    texto(app, "Mapa").set_value("Mirage")
    for label, value in [("Kills", 20), ("Deaths", 10), ("Assists", 5),
                         ("Headshots", 10), ("Damage", 2000), ("KAST Rounds", 15)]:
        numero(app, label).set_value(value)
    botao(app, "Salvar partida").click().run()
    assert not app.exception
    assert any("registradas com sucesso" in s.value for s in app.success)
    metricas = {m.label: m.value for m in app.metric}
    assert metricas["Partidas"] == "1"
    assert metricas["K/D"] == "2.00"
    assert metricas["ADR"] == "100.00"
    assert metricas["Win Rate"] == "100.00%"
    assert metricas["Best Map"] == metricas["Worst Map"] == "de_mirage"
    assert any("coincidem" in i.value for i in app.info)
    historico = app.dataframe[0].value
    assert historico.iloc[0]["Mapa"] == "de_mirage"
    assert historico.iloc[0]["Resultado"] == "Vitória"
    assert historico.iloc[0]["Kills"] == 20
    with abrir_banco() as conn:
        antes = dados(conn)
    app.run()
    app.run()
    with abrir_banco() as conn:
        assert dados(conn) == antes
    assert all(b.label != "Salvar partida" for b in app.button)
    botao(app, "Registrar outra partida").click().run()
    assert texto(app, "Mapa").value == ""
    app.run()
    with abrir_banco() as conn:
        assert dados(conn) == antes


def test_performance_invalida_mostra_orientacao(app_env):
    app = iniciar()
    cadastrar(app, "eu")
    texto(app, "Mapa").set_value("Mirage")
    numero(app, "Headshots").set_value(1)
    botao(app, "Salvar partida").click().run()
    assert not app.exception
    assert any("Headshots" in e.value for e in app.error)
    with abrir_banco() as conn:
        assert conn.execute("SELECT COUNT(*) FROM partida").fetchone() == (0,)


def test_selecao_isolamento_best_worst_e_ordem_historico(app_env):
    with abrir_banco() as conn:
        eu = cadastrar_jogador(conn, "eu")
        colega = cadastrar_jogador(conn, "colega")
        stats = dict(kills=20, deaths=10, assists=5, headshots=10, damage=2000,
                     utility_damage=0, enemies_blinded=0, flash_assists=0,
                     first_kills=0, first_deaths=0, kast_rounds=15)
        salvar_partida_completa(conn, eu, date(2026, 10, 29), "Mirage", 13, 7, stats)
        salvar_partida_completa(conn, eu, date(2026, 10, 29), "Nuke", 7, 13, stats)
    app = iniciar()
    app.selectbox(key="jogador").select(eu).run()
    metricas = {m.label: m.value for m in app.metric}
    assert metricas["Best Map"] == "de_mirage"
    assert metricas["Worst Map"] == "de_nuke"
    assert list(app.dataframe[0].value["Mapa"]) == ["de_nuke", "de_mirage"]
    app.selectbox(key="jogador").select(colega).run()
    assert not app.exception
    assert not app.metric
    assert not app.dataframe
    assert any("ainda não tem partidas" in i.value for i in app.info)
    with abrir_banco() as conn:
        assert conn.execute("SELECT COUNT(*) FROM partida").fetchone() == (2,)


def test_erro_banco_amigavel(app_env, monkeypatch):
    monkeypatch.setenv("CS2_DB_PATH", str(app_env.parent))  # Diretório não é banco.
    app = iniciar()
    assert any("Não foi possível acessar" in e.value for e in app.error)
