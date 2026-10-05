import re
import pytest
from pathlib import Path

from trab_final.helper import extrair_valores

RECUSA = re.compile(
    r"não\s+(?:está|estão|esta)\s+disponíve(?:l|is)"
    r"|não\s+(?:tenho|possuo|encontrei|há)\s+(?:essa|esta|essas|estas)?\s*informaç",
    re.IGNORECASE,
)

DOCS = Path(__file__).resolve().parents[1] / "docs"

VALOR = re.compile(r"R\$\s*\d|\d+(?:,\d+)?\s*%|\d+\s*(?:dias|meses)", re.IGNORECASE)


def test_fora_do_escopo(perguntar_com_log):
    pergunta = "Qual é a taxa de juros do Banco Central que estava valendo para 2025?"
    resposta = perguntar_com_log(pergunta)
    texto = resposta["message"]

    assert RECUSA.search(texto), f"sem recusa explícita: {texto}"

    inventados = VALOR.findall(texto)
    assert not inventados, f"valores citados numa resposta fora do escopo: {inventados}"


@pytest.fixture(scope="module")
def valores_dos_documentos() -> set[str]:
    texto = "\n".join(p.read_text(encoding="utf-8") for p in DOCS.glob("*.md"))
    return extrair_valores(texto)

@pytest.mark.parametrize("pergunta", [
    "Quais são todas as tarifas do cartão de crédito?",
    "Quais são as faixas de limite inicial do cartão?",
    "Quais são os prazos para contestar uma cobrança e para a ouvidoria responder?",
])
def test_valores_citados_existem_nos_documentos(perguntar_com_log, valores_dos_documentos, pergunta):
    texto = perguntar_com_log(pergunta)["message"]

    citados = extrair_valores(texto)
    inventados = citados - valores_dos_documentos

    assert citados, f"resposta sem nenhum valor — pergunta não exercitou o teste: {texto}"
    assert not inventados, f"valores fora dos documentos: {sorted(inventados)}"