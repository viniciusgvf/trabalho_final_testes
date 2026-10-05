import json
import os
import time
from datetime import datetime

from trab_final import RAIZ, login, perguntar

GOLDEN = RAIZ / "golden" / "golden_dataset.json"


def main() -> None:
    with open(GOLDEN, encoding="utf-8") as f:
        dataset = json.load(f)

    token = login(os.environ["AURA_USUARIO"], os.environ["AURA_SENHA"])

    for item in dataset["itens"]:
        if item.get("resposta_gravada") is not None:
            continue 

        resposta = perguntar(token, item["pergunta"], cache=False)

        item["resposta_gravada"] = {
            "message": resposta["message"],
            "sources": resposta.get("sources", []),
        }
        item["gravado_em"] = datetime.now().isoformat(timespec="seconds")
        print("gravado:", item["id"])

        time.sleep(3.5)  # margem para o limite de 20 req/min

    dataset["atualizado_em"] = datetime.now().isoformat(timespec="seconds")

    with open(GOLDEN, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()