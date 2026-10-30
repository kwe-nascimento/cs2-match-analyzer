"""Catálogo e validação de mapas do formulário; independente de Active Duty.

Para ampliar, adicione (nome amigável, identificador canônico) ao catálogo.
Não muda a normalização pública dos serviços nem registros existentes.
"""

from difflib import get_close_matches
import re

from src.app_servicos import normalizar_mapa

CATALOGO_MAPAS = (
    ("Mirage", "de_mirage"),
    ("Inferno", "de_inferno"),
    ("Nuke", "de_nuke"),
    ("Dust II", "de_dust2"),
    ("Ancient", "de_ancient"),
    ("Anubis", "de_anubis"),
    ("Cache", "de_cache"),
    ("Train", "de_train"),
    ("Overpass", "de_overpass"),
    ("Vertigo", "de_vertigo"),
    ("Office", "cs_office"),
)
OUTRO_MAPA = "__personalizado__"
NOMES_MAPAS = {identificador: nome for nome, identificador in CATALOGO_MAPAS}


def _chave(nome: str) -> str:
    nome = re.sub(r"^(?:de|cs)[_\s-]+", "", nome.strip().lower())
    return re.sub(r"[_\s-]+", "", nome)


def resolver_mapa_formulario(selecao: str | None, personalizado: str = "") -> str:
    """Retorna ID oficial ou mapa custom normalizado; ValueError orienta a UI.

    Nomes/IDs oficiais exatos no campo personalizado convergem ao catálogo.
    Similaridade >= 0.8 com nome/ID oficial exige seleção explícita no seletor;
    nunca corrige automaticamente uma aproximação. A regra só vale no formulário.
    """
    if selecao is None:
        raise ValueError("Selecione o mapa da partida.")
    if selecao in NOMES_MAPAS:
        return selecao
    if selecao != OUTRO_MAPA:
        raise ValueError("Selecione um mapa válido no catálogo.")
    normalizado = normalizar_mapa(personalizado)
    aliases = {_chave(valor): identificador
               for nome, identificador in CATALOGO_MAPAS
               for valor in (nome, identificador)}
    chave = _chave(personalizado)
    if chave in aliases:
        return aliases[chave]
    proximos = get_close_matches(chave, aliases, n=1, cutoff=0.8)
    if proximos:
        nome = NOMES_MAPAS[aliases[proximos[0]]]
        raise ValueError(f'O nome informado é parecido com {nome}. Se esse é o mapa desejado, selecione "{nome}" no campo Mapa; para um mapa personalizado, use um nome distinto.')
    return normalizado
