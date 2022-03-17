
import pytest
import rdflib
from pyshacl import validate
from ontotools.functions.validate import validate_syntax

from manifests import test_cases


@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_valid(name, invalid, shapes, valid, expected):
    r = validate(valid, shacl_graph=shapes, advanced=True)
    conforms, _, _ = r
    assert conforms == True


@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_invalid(name, invalid, shapes, valid, expected):
    r = validate(invalid, shacl_graph=shapes, advanced=True)
    _, results_graph, _ = r
    errors_num = int(results_graph.query(q).bindings[0][rdflib.term.Variable("count")])
    assert errors_num == expected


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


q = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT (count(distinct ?result) AS ?count)
    WHERE {
        ?graph a sh:ValidationReport ;
               sh:conforms false ;
               sh:result ?result .
    }
"""
