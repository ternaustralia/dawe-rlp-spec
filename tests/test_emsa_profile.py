"""Checks that the EMSA profile relaxes the TERN Ontology shapes as intended.

The TERN Ontology shapes are maintained in a separate repository, so these tests are
skipped unless a local copy is available. Set TERN_SHAPES to point at `tern.shapes.ttl`,
or check out `ontology_tern` next to this repository.
"""

import os
from pathlib import Path

import pytest
import rdflib
from pyshacl import validate

REPO_ROOT = Path(__file__).resolve().parents[1]
EMSA_SHAPES = REPO_ROOT / "shapes" / "emsa-profile" / "emsa-shapes.ttl"
VALID_DATA = REPO_ROOT / "shapes" / "emsa-profile" / "valid.ttl"

DEFAULT_TERN_SHAPES = REPO_ROOT.parent / "ontology_tern" / "docs" / "tern.shapes.ttl"
TERN_SHAPES = Path(os.environ.get("TERN_SHAPES", DEFAULT_TERN_SHAPES))

requires_tern_shapes = pytest.mark.skipif(
    not TERN_SHAPES.is_file(),
    reason=f"TERN Ontology shapes not found at {TERN_SHAPES}",
)


def _merged_shapes() -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(TERN_SHAPES)
    graph.parse(EMSA_SHAPES)
    return graph


@requires_tern_shapes
def test_emsa_exceptions_conform_with_tern_shapes():
    """The EMSA exceptions are accepted when the profile is loaded with the TERN shapes."""
    conforms, _, results_text = validate(
        rdflib.Graph().parse(VALID_DATA),
        shacl_graph=_merged_shapes(),
        advanced=True,
    )
    assert conforms, results_text


@requires_tern_shapes
def test_tern_shapes_alone_reject_the_emsa_exceptions():
    """Without the profile the same data fails, which is why the profile has to be loaded."""
    conforms, _, _ = validate(
        rdflib.Graph().parse(VALID_DATA),
        shacl_graph=rdflib.Graph().parse(TERN_SHAPES),
        advanced=True,
    )
    assert not conforms


@requires_tern_shapes
def test_deactivated_tern_shapes_are_restated():
    """Every TERN shape the profile deactivates is replaced by an EMSA shape on the same path."""
    sh = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    emsa = rdflib.Graph().parse(EMSA_SHAPES)
    tern = rdflib.Graph().parse(TERN_SHAPES)

    deactivated = set(emsa.subjects(sh.deactivated, rdflib.Literal(True)))
    assert deactivated, "The profile is expected to deactivate at least one TERN shape"

    emsa_paths = set(emsa.objects(None, sh.path))
    for shape in deactivated:
        path = tern.value(shape, sh.path)
        assert path is not None, f"{shape} is not a TERN property shape"
        assert path in emsa_paths, f"{shape} is deactivated but no EMSA shape restates {path}"
