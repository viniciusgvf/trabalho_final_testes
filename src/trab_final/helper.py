import re


def _normalizar(n: str) -> str:
    n = n.replace(".", "")
    if n.endswith(",00"):
        n = n[:-3]
    return n


def extrair_reais(texto: str) -> set[str]:
    valores_encontrados = set()

    valores_em_reais = re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", texto)

    for valor_bruto in valores_em_reais:
        valor_normalizado = _normalizar(valor_bruto)
        valores_encontrados.add(valor_normalizado)

    return valores_encontrados


def extrair_valores(texto: str) -> set[str]:
    valores_encontrados = set()

    valores_em_reais = re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", texto)
    valores_percentuais = re.findall(r"([\d.]+(?:,\d+)?)\s*%", texto)
    valores_prazo = re.findall(r"\b(\d+)\s*(?:dias|meses|anos)\b", texto, flags=re.IGNORECASE)

    todos_os_valores = valores_em_reais + valores_percentuais + valores_prazo

    for valor_bruto in todos_os_valores:
        valor_normalizado = _normalizar(valor_bruto)
        valores_encontrados.add(valor_normalizado)

    return valores_encontrados