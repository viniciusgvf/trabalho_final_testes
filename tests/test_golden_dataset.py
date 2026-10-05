import json
import re

import pytest

from trab_final import RAIZ

GOLDEN = RAIZ / "golden" / "golden_dataset.json"

with open(GOLDEN, encoding="utf-8") as f:
    DATASET = json.load(f)

ITENS = DATASET["itens"]
IDS = [item["id"] for item in ITENS]


def verificar_item(item: dict, resposta: dict) -> None:
    texto = resposta["message"]

    for padrao in item["fatos_esperados"]:
        assert re.search(padrao, texto, re.IGNORECASE), f"fato esperado ausente: {padrao}"

    for padrao in item["fatos_proibidos"]:
        encontrado = re.search(padrao, texto, re.IGNORECASE)
        assert encontrado is None, f"fato proibido presente: '{encontrado.group(0)}'"

    fonte_esperada = item["fonte_principal"]
    if fonte_esperada is not None:
        fontes = resposta.get("sources", [])
        assert fontes and fontes[0] == fonte_esperada, (
            f"fonte principal esperada {fonte_esperada}, recebida {fontes}"
        )


@pytest.mark.parametrize("item", ITENS, ids=IDS)
def test_golden_gravado(request, item):
    """Suíte normal: valida a resposta GRAVADA no golden. Nenhuma chamada à API."""
    resposta = item["resposta_gravada"]
    if resposta is None:
        pytest.skip("item sem resposta gravada — rode trab_final.gravar_golden")

    # registra no log de execução (o hook do conftest lê request.node.interacoes)
    request.node.interacoes = [[item["pergunta"], {**resposta, "_origem": "golden"}]]

    verificar_item(item, resposta)


@pytest.mark.live
@pytest.mark.parametrize("item", ITENS, ids=IDS)
def test_golden_ao_vivo(perguntar_com_log, item):
    """Regressão: mesma pergunta contra a AURA no ar, mesmos fatos esperados."""
    resposta = perguntar_com_log(item["pergunta"], cache=False)

    verificar_item(item, resposta)