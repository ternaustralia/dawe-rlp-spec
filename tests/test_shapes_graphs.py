"""Checks the generated sg.ttl files and the shape IRIs. Regenerate with `make shapes-graphs`."""

import importlib.util
import re
import uuid
from collections import Counter, defaultdict
from pathlib import Path

import pytest
from rdflib import Graph, RDF, SH, URIRef

REPO_ROOT = Path(__file__).resolve().parents[1]
SHAPES_ROOT = REPO_ROOT / "shapes"

_spec = importlib.util.spec_from_file_location("make_shapes_graphs", REPO_ROOT / "make-shapes-graphs.py")
make_shapes_graphs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_shapes_graphs)

UUID_PATTERN = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
SHAPE_IRI = re.compile(rf"https://linked\.data\.gov\.au/def/nrm/validator/shape/{UUID_PATTERN}")

UUID_FOLDERS = sorted(path.parent for path in SHAPES_ROOT.rglob("uuid.txt"))
SHAPES_FILES = sorted(SHAPES_ROOT.rglob("*shapes.ttl"))


def _folder_id(folder):
    return str(folder.relative_to(REPO_ROOT))


def _shape_iris(graph):
    shapes = set(graph.subjects(RDF.type, SH.NodeShape)) | set(graph.subjects(RDF.type, SH.PropertyShape))
    return {shape for shape in shapes if isinstance(shape, URIRef)}


@pytest.fixture(scope="module")
def built_shapes_graphs():
    return make_shapes_graphs.build_all(SHAPES_ROOT)


@pytest.mark.parametrize("folder", UUID_FOLDERS, ids=_folder_id)
def test_shapes_graph_is_up_to_date(folder, built_shapes_graphs):
    graph, _, _ = built_shapes_graphs[folder]
    committed = Graph().parse(folder / "sg.ttl")
    assert make_shapes_graphs.same_content(graph, committed), (
        f"{folder / 'sg.ttl'} is out of date, run `make shapes-graphs`"
    )


@pytest.mark.parametrize("folder", UUID_FOLDERS, ids=_folder_id)
def test_shapes_graph_iri_comes_from_uuid(folder):
    graph = Graph().parse(folder / "sg.ttl")
    declared = set(graph.subjects(RDF.type, make_shapes_graphs.SHAPES_GRAPH))
    assert declared == {make_shapes_graphs.graph_iri(folder)}


def test_shapes_graph_uuids_are_valid_and_unique():
    values = [(folder / "uuid.txt").read_text().strip() for folder in UUID_FOLDERS]
    invalid = [value for value in values if str(uuid.UUID(value)) != value]
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    assert not invalid, f"uuid.txt values that are not lower-case UUIDs: {invalid}"
    assert not duplicates, f"uuid.txt values used by more than one folder: {duplicates}"


def test_shape_iris_follow_the_uuid_pattern():
    bad = defaultdict(list)
    for path in SHAPES_FILES:
        for shape in _shape_iris(Graph().parse(path)):
            if not SHAPE_IRI.fullmatch(str(shape)):
                bad[str(path.relative_to(REPO_ROOT))].append(str(shape))
    assert not bad, f"Shapes with IRIs outside the UUID pattern: {dict(bad)}"


def test_each_shape_iri_has_one_definition():
    """Copies of a shape across property, protocol and module files must be identical."""
    definitions = defaultdict(dict)
    for path in SHAPES_FILES:
        graph = Graph().parse(path)
        for shape in _shape_iris(graph):
            definitions[shape][path] = repr(make_shapes_graphs.signature(graph.cbd(shape)))
    conflicting = {
        str(shape): sorted(str(path.relative_to(REPO_ROOT)) for path in copies)
        for shape, copies in definitions.items()
        if len(set(copies.values())) > 1
    }
    assert not conflicting, f"Shape IRIs with different definitions in different files: {conflicting}"
