import json
from py import test
from pyshacl import validate
import re

with open("tests/test.json") as f:
    data = json.loads(f.read())


def test_valid():
    for i in data:
        data_graph = i["valid_tests"]
        sg = i["shapes"]
        r = validate(data_graph, shacl_graph=sg, advanced=True)
        conforms, results_graph, results_text = r
        assert conforms == True


def test_invalid():
    for i in data:
        data_graph = i["invalid_tests"]
        sg = i["shapes"]
        r = validate(data_graph, shacl_graph=sg, advanced=True)
        conforms, results_graph, results_text = r
        results_text = results_text.splitlines()[2]
        errors_num = int(re.findall(r"\d+", results_text)[0])
        assert errors_num == i["expected_failures"]
