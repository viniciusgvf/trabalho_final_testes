import json
import os
from datetime import datetime
from pathlib import Path
from typing import Callable

import requests

BASE = "https://assistente-financeiro-testes.onrender.com"
TIMEOUT = 180  # a primeira chamada depois de o servidor hibernar pode passar de 2 minutos

RAIZ = Path(__file__).resolve().parents[2]   # src/trab_final/__init__.py -> raiz do projeto
MEMORIES = RAIZ / "memories.json"
LOG = RAIZ / "execucao.log"

def _chave(pergunta: str, history: list | None) -> str:
    # sem history, a chave é a própria pergunta; com history, a mesma pergunta é outro prompt
    if not history:
        return pergunta
    return json.dumps({"pergunta": pergunta, "history": history},
                      ensure_ascii=False, sort_keys=True)

def _ler_memories() -> dict:
    if not MEMORIES.exists():
        return {}
    return json.loads(MEMORIES.read_text(encoding="utf-8"))

def _gravar_memory(pergunta: str, history: list | None, dados: dict) -> None:
    mem = _ler_memories()
    mem[_chave(pergunta, history)] = {
        "pergunta": pergunta,
        "history": history or [],
        "gravado_em": datetime.now().isoformat(timespec="seconds"),
        "resposta": dados,
    }
    MEMORIES.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")

def login(usuario: str, senha: str) -> str:
    r = requests.post(f"{BASE}/auth/login",
                      json={"username": usuario, "password": senha},
                      timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["access_token"]


def perguntar(token: str, pergunta: str,  history: list | None = None,cache:bool = True) -> dict:
    
    if cache:
        memo = _ler_memories().get(_chave(pergunta, history))
        if memo:
            return {**memo["resposta"], "_origem": "Cache"}
        return perguntar(token, pergunta,  history, cache=False)


    r = requests.post(f"{BASE}/chat",
                      json={"message": pergunta, "history": history or []},
                      headers={"Authorization": f"Bearer {token}"},
                      stream=True, timeout=TIMEOUT)
    r.raise_for_status()
    for linha in r.iter_lines(decode_unicode=True):
        if linha and linha.startswith("data:"):
            dados = json.loads(linha[len("data:"):].strip())
            if "message" in dados:
                _gravar_memory(pergunta, history, dados)
                return dados
    raise RuntimeError("stream terminou sem resposta")

def registrar_log(teste: str, pergunta: str, resposta: dict,
                  resultado: str, erro: str | None = None) -> None:
    linhas = [
        f"data_hora : {datetime.now().isoformat(sep=' ', timespec='seconds')}",
        f"teste     : {teste}",
        f"resultado : {resultado}",
        f"pergunta  : {pergunta}",
        f"resposta  : {resposta.get('message', '-')}",
        f"origem    : {resposta.get('_origem', 'API')}",
        f"sources   : {json.dumps(resposta.get('sources'), ensure_ascii=False)}",
        "=" * 80,
    ]
    if erro:
        linhas.append(f"erro      : {erro}")
    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")

def main() -> None:
    print("Hello from trab-final!")
    token = login(os.environ["AURA_USUARIO"], os.environ["AURA_SENHA"])
    resposta = perguntar(token, "Qual é a anuidade do cartão?", cache=False)
    print(resposta["message"])
    print(resposta["sources"])
