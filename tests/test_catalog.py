from euri_codegen.catalog_loader import load_catalog


def test_catalog_loads():
    data = load_catalog()
    assert isinstance(data, list) and len(data) >= 1
    assert any(item.get("id") == "binary_search" for item in data)
