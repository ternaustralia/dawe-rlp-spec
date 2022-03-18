import pytest
from ontotools.functions.validate import validate_syntax

from manifests import test_cases

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_validate_valid(name, invalid, shapes, valid, expected):
    with open(valid, "r") as f:
        data = f.read()
        result = validate_syntax(data, "turtle")
        assert result == True


@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_validate_invalid(name, invalid, shapes, valid, expected):
    with open(invalid, "r") as f:
        data = f.read()
        result = validate_syntax(data, "turtle")
        assert result == True


@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_validate_shapes(name, invalid, shapes, valid, expected):
    with open(shapes, "r") as f:
        data = f.read()
        result = validate_syntax(data, "turtle")
        assert result == True