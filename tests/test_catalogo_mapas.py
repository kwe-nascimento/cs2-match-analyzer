"""Catálogo do formulário sem alterar a API de normalização existente."""
import pytest

from src.app_servicos import normalizar_mapa
from src.catalogo_mapas import CATALOGO_MAPAS, OUTRO_MAPA, resolver_mapa_formulario


def test_catalogo_contem_mapeamento_solicitado():
    assert dict(CATALOGO_MAPAS) == {
        "Mirage": "de_mirage", "Inferno": "de_inferno", "Nuke": "de_nuke",
        "Dust II": "de_dust2", "Ancient": "de_ancient", "Anubis": "de_anubis",
        "Cache": "de_cache", "Train": "de_train", "Overpass": "de_overpass",
        "Vertigo": "de_vertigo", "Office": "cs_office",
    }


@pytest.mark.parametrize("nome,identificador", CATALOGO_MAPAS)
def test_selecao_oficial_usa_id_independente_do_custom(nome, identificador):
    assert resolver_mapa_formulario(identificador, "mirrage") == identificador


@pytest.mark.parametrize("entrada,id", [
    ("Mirage", "de_mirage"), (" DE MIRAGE ", "de_mirage"),
    ("Dust II", "de_dust2"), ("dust2", "de_dust2"), ("de_dust2", "de_dust2"),
    ("Office", "cs_office"), ("de_office", "cs_office"), ("CS-OFFICE", "cs_office"),
])
def test_custom_oficial_exato_converge_ao_catalogo(entrada, id):
    assert resolver_mapa_formulario(OUTRO_MAPA, entrada) == id


@pytest.mark.parametrize("entrada", [" aim_custom ", "  Minha   Arena  ", "de_mirage_custom", "cs_meu_mapa"])
def test_custom_usa_normalizacao_existente(entrada):
    assert resolver_mapa_formulario(OUTRO_MAPA, entrada) == normalizar_mapa(entrada)


@pytest.mark.parametrize("entrada", ["mirrage", "de_mirgae", "infernu", "dust22", "ofice"])
def test_erro_obvio_sugere_selecao_sem_correcao_silenciosa(entrada):
    with pytest.raises(ValueError, match="parecido.*selecione"):
        resolver_mapa_formulario(OUTRO_MAPA, entrada)


@pytest.mark.parametrize("entrada", ["", "   "])
def test_custom_vazio(entrada):
    with pytest.raises(ValueError, match="mapa"):
        resolver_mapa_formulario(OUTRO_MAPA, entrada)


@pytest.mark.parametrize("selecao,mensagem", [(None, "Selecione o mapa"), ("inexistente", "catálogo")])
def test_selecao_obrigatoria_e_controlada(selecao, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        resolver_mapa_formulario(selecao)


def test_servicos_preservam_comportamento_anterior():
    # Chamadas diretas continuam aceitando texto livre sem a regra do formulário.
    assert normalizar_mapa("Office") == "de_office"
    assert normalizar_mapa("Dust II") == "dust_ii"
    assert normalizar_mapa("mirrage") == "de_mirrage"
