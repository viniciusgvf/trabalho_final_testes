import os
import pytest

from datetime import datetime
from pathlib import Path
import re
import json

from trab_final import LOG


#inicio de testes
with LOG.open("a", encoding="utf-8") as f:
    f.write("\n",)
    f.write("#" * 80,)
    f.write("\n",)
    f.write("# INICIO DE TESTES: "+ datetime.now().isoformat(sep=' ', timespec='seconds'))
    f.write("\n",)
    f.write("#" * 80,)
    f.write("\n",)

def test_anuidade_cartao_padrao(perguntar_com_log):
    pergunta =  "Qual é a anuidade do cartão?"
    resposta = perguntar_com_log(pergunta)
    texto = resposta["message"]

    assert re.search(r"\b240(?:,00)?\b|\b20,00\b", texto), texto

    fonte = resposta.get("sources", [])[0].lower()
    assert ("tarifas-cartao.md" == fonte), "Fonte principal errada."

def test_prazo_analise_credito(perguntar_com_log):
    pergunta = "Quanto tempo demora a análise de crédito para o cartão?"
    resposta = perguntar_com_log(pergunta)
    texto = resposta["message"]

    assert re.search(r"\b(?:5|cinco)\s*(?:\(cinco\)\s*)?dias\s+úteis", texto, re.IGNORECASE), texto

    fonte = resposta.get("sources", [])[0].lower()
    assert ("politica-credito.md" == fonte), "Fonte principal errada."


def verifica_trecho_json(texto: str) -> str | None:
    conteudo = texto.strip()

    if conteudo.startswith("```"):
        conteudo = conteudo.strip("`")
        if conteudo.startswith("json"):
            conteudo = conteudo[len("json"):]
        conteudo = conteudo.strip()

    envelope_vazou = conteudo.startswith("{") or '"message":' in conteudo
    if not envelope_vazou:
        return None

    try:
        json.loads(conteudo)
        return "envelope JSON completo vazou para o message"
    except json.JSONDecodeError:
        return "envelope JSON TRUNCADO vazou para o message"


PERGUNTAS_TAMANHO = [
    "Qual é a anuidade do cartão?",
    "Quais são todas as tarifas do cartão de crédito?",
    "Explique em detalhes, item por item, toda a política de crédito: critérios de elegibilidade, "
    "faixas de limite inicial com um exemplo para cada faixa, documentos exigidos e prazo de análise.",
    "Com o máximo de detalhes possível, descreva tudo o que você sabe sobre o cartão Aurora: "
    "todas as tarifas, critérios de crédito, faixas de limite, regras de aumento de limite, "
    "cancelamento, contestação de cobrança, ouvidoria e canais de atendimento.",
]
IDS_TAMANHO = ["controle_curta", "media_tarifas", "longa_politica", "exaustiva_tudo"]


@pytest.mark.parametrize("pergunta", PERGUNTAS_TAMANHO, ids=IDS_TAMANHO)
def test_resposta_longa_nao_quebra_formato(perguntar_com_log, pergunta):
    texto = perguntar_com_log(pergunta)["message"]

    problema = verifica_trecho_json(texto)

    assert problema is None, f"{problema} (tamanho do message: {len(texto)} caracteres)"