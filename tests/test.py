import pytest
import rdflib
from pyshacl import validate

from manifests import test_cases

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_valid(name, invalid, shapes, valid, expected):
    r = validate(valid, shacl_graph=shapes, advanced=True)
    conforms, results_graph, results_text = r
    assert conforms == True

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", test_cases)
def test_invalid(name, invalid, shapes, valid, expected):
    r = validate(invalid, shacl_graph=shapes, advanced=True)
    conforms, results_graph, results_text = r
    errors_num = int(results_graph.query(q).bindings[0][rdflib.term.Variable('count')])
    assert errors_num == expected

q = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    SELECT (count(distinct ?result) AS ?count)
    WHERE {
        ?graph a sh:ValidationReport ;
               sh:conforms false ;
               sh:result ?result .
    }
"""
