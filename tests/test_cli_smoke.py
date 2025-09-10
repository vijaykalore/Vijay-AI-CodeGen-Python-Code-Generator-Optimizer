import importlib


def test_cli_module_entrypoint():
    # Ensure the package exposes __main__ and cli
    m = importlib.import_module("euri_codegen.__main__")
    assert hasattr(m, "main")
