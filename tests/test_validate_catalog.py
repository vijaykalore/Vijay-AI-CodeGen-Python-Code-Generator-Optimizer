from euri_codegen.catalog_loader import load_catalog
from euri_codegen.models import validate_specs


def test_validate_catalog():
    data = load_catalog()
    specs = validate_specs(data)
    assert len(specs) >= 1
