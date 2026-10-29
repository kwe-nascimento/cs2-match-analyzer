"""Persistência e validação amigável para o MVP visual, sem dependência da UI."""

from contextlib import contextmanager
from datetime import date
import os
from pathlib import Path
import sqlite3

from src.db import connect, init_db
from src.registros import registrar_partida, registrar_performance

ROOT = Path(__file__).resolve().parents[1]


def caminho_banco() -> Path:
    """Caminhos relativos, inclusive CS2_DB_PATH, partem da raiz do projeto."""
    path = Path(os.environ.get("CS2_DB_PATH", "data/cs2.sqlite")).expanduser()
    return path if path.is_absolute() else ROOT / path


@contextmanager
def abrir_banco():
    """Uma conexão por uso; inicializa e fecha inclusive quando ocorre erro."""
    path = caminho_banco()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(str(path))
    try:
        init_db(conn)
        yield conn
    finally:
        conn.close()


def listar_jogadores(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute("SELECT player_id, nickname FROM player ORDER BY nickname, player_id").fetchall()


def cadastrar_jogador(conn: sqlite3.Connection, nickname: str, steam_id: str = "") -> int:
    """Cadastro confirmado pelo serviço; whitespace opcional vira NULL."""
    nickname = nickname.strip()
    if not nickname:
        raise ValueError("Informe um nickname que não contenha apenas espaços.")
    if conn.in_transaction:
        raise ValueError("Conclua a transação anterior antes de cadastrar o jogador.")
    with conn:
        cursor = conn.execute(
            "INSERT INTO player (nickname, steam_id) VALUES (?, ?)",
            (nickname, steam_id.strip() or None),
        )
    return cursor.lastrowid


def normalizar_mapa(mapa: str) -> str:
    """Minúsculas, espaços como _, prefixo de_ em nomes simples; aceita customizados."""
    nome = "_".join(mapa.strip().lower().split())
    if not nome:
        raise ValueError("Informe o mapa da partida.")
    return nome if "_" in nome else "de_" + nome


def validar_formulario(data_partida: date, mapa: str, rounds_time: int,
                       rounds_adversario: int, performance: dict) -> list[str]:
    """Retorna orientações da UI; o schema continua sendo a proteção definitiva."""
    erros = []
    if not isinstance(data_partida, date):
        erros.append("Informe uma data válida.")
    if not mapa.strip():
        erros.append("Informe o mapa da partida.")
    rounds = rounds_time + rounds_adversario
    if rounds_time < 0 or rounds_adversario < 0 or any(v < 0 for v in performance.values()):
        erros.append("Os valores numéricos não podem ser negativos.")
    if rounds <= 0:
        erros.append("O total de rounds deve ser maior que zero.")
    for campo, limite, mensagem in [
        ("headshots", performance["kills"], "Headshots não podem superar kills."),
        ("first_kills", performance["kills"], "First Kills não podem superar kills."),
        ("first_deaths", performance["deaths"], "First Deaths não podem superar deaths."),
        ("kast_rounds", rounds, "KAST Rounds não podem superar o total de rounds."),
    ]:
        if performance[campo] > limite:
            erros.append(mensagem)
    if performance["first_kills"] + performance["first_deaths"] > rounds:
        erros.append("First Kills + First Deaths não podem superar o total de rounds.")
    return erros


def salvar_partida_completa(conn: sqlite3.Connection, player_id: int,
                            data_partida: date, mapa: str, rounds_time: int,
                            rounds_adversario: int, performance: dict) -> int:
    """Grava partida e performance atomicamente; falhas do schema fazem rollback.

    Recebe uma conexão sem outra transação pendente. O chamador apresenta as
    mensagens amigáveis de validar_formulario; constraints SQLite sempre valem.
    """
    if conn.in_transaction:
        raise ValueError("Conclua a transação anterior antes de registrar a partida.")
    mapa = normalizar_mapa(mapa)
    resultado = "vitoria" if rounds_time > rounds_adversario else "derrota" if rounds_time < rounds_adversario else "empate"
    with conn:
        partida_id = registrar_partida(
            conn, data_partida.isoformat(), mapa, resultado, rounds_time, rounds_adversario,
        )
        registrar_performance(
            conn, player_id=player_id, partida_id=partida_id,
            rounds_played=rounds_time + rounds_adversario, **performance,
        )
    return partida_id
