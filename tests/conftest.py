import pytest
import os

from trab_final import login, registrar_log, perguntar


@pytest.fixture(scope="session")
def token() -> str:
    return login(os.environ["AURA_USUARIO"], os.environ["AURA_SENHA"])

@pytest.fixture(scope="session")
def use_memory() -> bool:
    return os.environ["AURA_MEMO"] == "1"

@pytest.fixture
def perguntar_com_log(request, token,use_memory):
    """Wrapper de perguntar() que guarda as interações do teste para o log."""
    interacoes: list[list] = []
    request.node.interacoes = interacoes
    print("Use_memory = ",use_memory)

    def _perguntar(pergunta: str, history: list | None = None, cache: bool | None = None) -> dict:
        usar_cache = use_memory if cache is None else cache
        registro = [pergunta, {}]
        interacoes.append(registro)
        registro[1] = perguntar(token, pergunta, cache=usar_cache, history=history)
        return registro[1]

    return _perguntar

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        nome_do_teste = item.name
        
        if report.passed:
            status = "SUCESSO"
            motivo = None
        elif report.failed:
            status = "FALHA"
            motivo = call.excinfo.exconly() if call.excinfo else None
        elif report.skipped:
            status = "PULADO"
            motivo = None
        else:
            status = "DESCONHECIDO"
            motivo = None

        for pergunta, resposta in getattr(item, 'interacoes', []):
            registrar_log(nome_do_teste
                        , pergunta
                        , resposta
                        , status
                        , motivo)
    return outcome