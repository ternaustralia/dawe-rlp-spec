import json
from pyshacl import validate
import re
import pytest
from data import properties
import rdflib

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", properties)
def test_valid(name, invalid, shapes, valid, expected):
    r = validate(valid, shacl_graph=shapes, advanced=True)
    conforms, results_graph, results_text = r
    assert conforms == True

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", properties)
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
