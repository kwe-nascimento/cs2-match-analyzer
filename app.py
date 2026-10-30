"""CS2 Match Analyzer — MVP visual 1. Execute com streamlit run app.py."""

from datetime import date
import logging
import sqlite3

import streamlit as st

from src.app_servicos import (
    abrir_banco, cadastrar_jogador, listar_jogadores,
    salvar_partida_completa, validar_formulario,
)
from src.consultas import listar_partidas
from src.evolucao import listar_evolucao, resumir_evolucao
from src.mapas import obter_estatisticas_mapas, obter_melhor_mapa, obter_pior_mapa
from src.metricas import obter_resumo_jogador

LOGGER = logging.getLogger(__name__)
CAMPOS = {
    "kills": "Kills", "deaths": "Deaths", "assists": "Assists",
    "headshots": "Headshots", "damage": "Damage",
    "utility_damage": "Utility Damage", "enemies_blinded": "Enemies Blinded",
    "flash_assists": "Flash Assists", "first_kills": "First Kills",
    "first_deaths": "First Deaths", "kast_rounds": "KAST Rounds",
}


def sidebar(conn):
    st.sidebar.title("CS2 Match Analyzer")
    st.sidebar.caption("MVP VISUAL 1 · SEU DESEMPENHO EM FOCO")
    with st.sidebar.form("cadastro_jogador", clear_on_submit=True):
        st.subheader("Novo jogador")
        nickname = st.text_input("Nickname", key="nickname")
        steam_id = st.text_input("Steam ID (opcional)", key="steam_id")
        cadastrar = st.form_submit_button("Cadastrar jogador", use_container_width=True)
    if cadastrar:
        try:
            novo_id = cadastrar_jogador(conn, nickname, steam_id)
        except ValueError as exc:
            st.sidebar.error(str(exc))
        except sqlite3.IntegrityError:
            st.sidebar.error("Nickname ou Steam ID já cadastrado. Escolha outro ou selecione o jogador existente.")
        else:
            st.session_state["jogador"] = novo_id
            st.session_state["mensagem"] = "Jogador cadastrado com sucesso."
            st.rerun()
    jogadores = listar_jogadores(conn)
    if not jogadores:
        st.sidebar.info("Cadastre seu primeiro jogador para começar.")
        return None
    nomes = dict(jogadores)
    if st.session_state.get("jogador") not in nomes:
        st.session_state["jogador"] = jogadores[0][0]
    player_id = st.sidebar.selectbox(
        "Jogador selecionado", options=list(nomes), format_func=nomes.get, key="jogador",
    )
    st.sidebar.divider()
    st.sidebar.caption("Dados salvos no SQLite local. Cada jogador tem seu próprio histórico e estatísticas.")
    return player_id


def formulario_partida(conn, player_id):
    st.subheader("Registrar partida")
    st.caption("Placar e desempenho são salvos juntos. O resultado e os rounds jogados são definidos automaticamente.")
    if st.session_state.get("partida_salva") == player_id:
        st.success("Partida e performance registradas com sucesso.")
        if st.button("Registrar outra partida", key="nova_partida", type="primary"):
            st.session_state.pop("partida_salva", None)
            st.session_state["form_geracao"] = st.session_state.get("form_geracao", 0) + 1
            st.rerun()
        return
    prefix = f"partida_{player_id}_{st.session_state.get('form_geracao', 0)}"
    with st.form(prefix):
        c1, c2 = st.columns(2)
        data_partida = c1.date_input("Data da partida", value=date.today(), key=prefix + "_data")
        mapa = c2.text_input("Mapa", placeholder="Ex.: Mirage, de_nuke ou aim_custom", key=prefix + "_mapa")
        c1, c2 = st.columns(2)
        rounds_time = c1.number_input("Rounds do time", min_value=0, value=13, step=1, key=prefix + "_time")
        rounds_adversario = c2.number_input("Rounds do adversário", min_value=0, value=7, step=1, key=prefix + "_adversario")
        st.caption("Nomes simples como Mirage viram de_mirage. Mapas personalizados são aceitos.")
        st.markdown("#### Performance individual")
        columns = st.columns(3)
        performance = {
            campo: columns[i % 3].number_input(label, min_value=0, value=0, step=1, key=prefix + "_" + campo)
            for i, (campo, label) in enumerate(CAMPOS.items())
        }
        salvar = st.form_submit_button("Salvar partida", type="primary", use_container_width=True)
    if salvar:
        erros = validar_formulario(data_partida, mapa, rounds_time, rounds_adversario, performance)
        if erros:
            for erro in erros:
                st.error(erro)
            return
        try:
            salvar_partida_completa(conn, player_id, data_partida, mapa, rounds_time, rounds_adversario, performance)
        except (sqlite3.IntegrityError, ValueError):
            st.error("Não foi possível salvar. Confira o jogador, a data, o placar e os limites da performance. Nenhuma partida foi gravada.")
        else:
            st.session_state["partida_salva"] = player_id
            st.rerun()


def visao_geral(conn, player_id):
    st.subheader("Seu desempenho")
    resumo = obter_resumo_jogador(conn, player_id)
    if resumo is None:
        st.info("Você ainda não tem partidas. Registre a primeira na aba Registrar partida.")
        return
    grupos = [
        [("partidas", "Partidas", ""), ("vitorias", "Vitórias", ""), ("derrotas", "Derrotas", ""), ("empates", "Empates", "")],
        [("kd", "K/D", ""), ("kda", "KDA", ""), ("adr", "ADR", "")],
        [("hs_percent", "HS%", "%"), ("kast_percent", "KAST%", "%"), ("win_rate", "Win Rate", "%")],
    ]
    for grupo in grupos:
        for coluna, (campo, titulo, sufixo) in zip(st.columns(len(grupo)), grupo):
            valor = str(resumo[campo]) if campo in {"partidas", "vitorias", "derrotas", "empates"} else f"{resumo[campo]:.2f}{sufixo}"
            coluna.metric(titulo, valor)
    st.caption("Métricas calculadas pelos totais. Valores arredondados somente nesta apresentação.")


def historico(conn, player_id):
    st.subheader("Histórico de partidas")
    partidas = listar_partidas(conn, player_id)
    if not partidas:
        st.info("Nenhuma partida registrada para este jogador.")
        return
    resultados = {"vitoria": "Vitória", "derrota": "Derrota", "empate": "Empate"}
    linhas = []
    for _, data, mapa, resultado, time, adversario, kills, deaths, assists, headshots in partidas:
        linhas.append({"Data": data, "Mapa": mapa, "Resultado": resultados[resultado],
                       "Placar": f"{time} × {adversario}", "Kills": kills, "Deaths": deaths,
                       "Assists": assists, "Headshots": headshots})
    st.dataframe(linhas, hide_index=True, use_container_width=True)
    st.caption("Mais recentes primeiro; em datas iguais, a última partida registrada aparece antes.")


def estatisticas_mapas(conn, player_id):
    st.subheader("Estatísticas por mapa")
    mapas = obter_estatisticas_mapas(conn, player_id)
    if not mapas:
        st.info("Seus mapas aparecerão aqui após o primeiro registro.")
        return
    best, worst = obter_melhor_mapa(conn, player_id), obter_pior_mapa(conn, player_id)
    for coluna, titulo, mapa in zip(st.columns(2), ["Best Map", "Worst Map"], [best, worst]):
        coluna.metric(titulo, mapa["mapa"])
        coluna.caption(f"{mapa['partidas']} partida(s) · Win Rate {mapa['win_rate']:.2f}%")
    if len(mapas) == 1:
        st.info("Com apenas um mapa, Best Map e Worst Map coincidem.")
    st.dataframe([
        {"Mapa": m["mapa"], "Partidas": m["partidas"], "Win Rate (%)": round(m["win_rate"], 2),
         "K/D": round(m["kd"], 2), "ADR": round(m["adr"], 2), "KAST (%)": round(m["kast_percent"], 2)}
        for m in mapas
    ], hide_index=True, use_container_width=True)
    st.caption("Classificação: Win Rate, ADR e K/D decrescentes; nome crescente. Amostras pequenas podem ser pouco representativas.")



def evolucao(conn, player_id):
    st.subheader("Evolução histórica")
    historico_completo = listar_evolucao(conn, player_id)
    if not historico_completo:
        st.info("Sua evolução aparecerá aqui após a primeira partida.")
        return
    # A assinatura renova padrões após registros novos; cada jogador tem filtros próprios.
    assinatura = f"evolucao_{player_id}_{len(historico_completo)}_{max(r['partida_id'] for r in historico_completo)}"
    mapas = sorted({r["mapa"] for r in historico_completo})
    c1, c2, c3 = st.columns(3)
    mapa = c1.selectbox("Mapa da evolução", [None, *mapas],
                        format_func=lambda m: "Todos" if m is None else m,
                        key=assinatura + "_mapa")
    inicio = c2.date_input("Data inicial", value=date.fromisoformat(historico_completo[0]["data_partida"]),
                           key=assinatura + "_inicio")
    fim = c3.date_input("Data final", value=date.fromisoformat(historico_completo[-1]["data_partida"]),
                        key=assinatura + "_fim")
    if inicio is None or fim is None or inicio > fim:
        st.warning("Informe um período válido: a data inicial deve ser anterior ou igual à data final.")
        return
    registros = listar_evolucao(conn, player_id, mapa, inicio, fim)
    resumo = resumir_evolucao(registros)
    if resumo is None:
        st.info("Nenhuma partida encontrada para os filtros selecionados.")
        return
    for coluna, campo, titulo, sufixo in zip(
        st.columns(4), ["partidas", "kd", "adr", "kast_percent"],
        ["Partidas filtradas", "K/D filtrado", "ADR filtrado", "KAST% filtrado"], ["", "", "", "%"],
    ):
        valor = str(resumo[campo]) if campo == "partidas" else f"{resumo[campo]:.2f}{sufixo}"
        coluna.metric(titulo, valor)
    st.caption("Indicadores calculados pelos totais filtrados; arredondamento apenas na apresentação.")
    linhas = [
        {"Ordem": i, "ID": r["partida_id"], "Data": r["data_partida"], "Mapa": r["mapa"],
         "Resultado": r["resultado"], "K/D": r["kd"], "ADR": r["adr"], "KAST%": r["kast_percent"]}
        for i, r in enumerate(registros, 1)
    ]
    if len(registros) == 1:
        st.info("Apenas uma partida no intervalo: os valores não indicam uma tendência estatística.")
    else:
        for campo in ["K/D", "ADR", "KAST%"]:
            st.markdown(f"#### Evolução de {campo} por partida")
            st.line_chart(linhas, x="Ordem", y=campo, color="#3b82f6")
    st.dataframe(linhas, hide_index=True, use_container_width=True)
    st.caption("Ordem cronológica crescente; datas iguais são desempatadas pelo ID da partida. Consulte datas e mapas pela ordem da tabela.")


def main():
    st.set_page_config(page_title="CS2 Match Analyzer", page_icon="🎯", layout="wide")
    try:
        with abrir_banco() as conn:
            player_id = sidebar(conn)
            st.title("CS2 Match Analyzer")
            st.caption("REGISTRE. COMPARE. EVOLUA.")
            if mensagem := st.session_state.pop("mensagem", None):
                st.success(mensagem)
            if player_id is None:
                st.info("Bem-vindo! Cadastre um jogador na barra lateral para acompanhar sua evolução.")
                return
            tabs = st.tabs(["Visão geral", "Registrar partida", "Histórico", "Estatísticas por mapa", "Evolução"])
            # Processa submissão antes de renderizar consultas: um rerun atualiza todas as abas.
            with tabs[1]:
                formulario_partida(conn, player_id)
            with tabs[0]:
                visao_geral(conn, player_id)
            with tabs[2]:
                historico(conn, player_id)
            with tabs[3]:
                estatisticas_mapas(conn, player_id)
            with tabs[4]:
                evolucao(conn, player_id)
    except (sqlite3.OperationalError, OSError):
        LOGGER.exception("Falha ao acessar o banco local")
        st.error("Não foi possível acessar o banco local. Verifique permissões, espaço disponível ou se outro processo está gravando e tente novamente.")


if __name__ == "__main__":
    main()
