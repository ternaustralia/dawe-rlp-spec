import json
from pyshacl import validate
import re
import pytest

with open("tests/test.json") as f:
    data = json.loads(f.read())

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", data)
def test_valid(name, invalid, shapes, valid, expected):
    r = validate(valid, shacl_graph=shapes, advanced=True)
    conforms, results_graph, results_text = r
    assert conforms == True

@pytest.mark.parametrize("name, shapes, valid, invalid, expected", data)
def test_invalid(name, invalid, shapes, valid, expected):
    r = validate(invalid, shacl_graph=shapes, advanced=True)
    conforms, results_graph, results_text = r
    results_text = results_text.splitlines()[2]
    errors_num = int(re.findall(r"\d+", results_text)[0])
    assert errors_num == expected
