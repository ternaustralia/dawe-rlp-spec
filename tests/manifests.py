from typing import List, Tuple
from dataclasses import dataclass, astuple


@dataclass
class TestCaseItem:
    name: str
    shapes_path: str
    valid_data_path: str
    invalid_data_path: str
    expected_failures: int

    def astuple(self) -> Tuple:
        return astuple(self)


test_cases: List[TestCaseItem] = [
    TestCaseItem(
        "plot-description-slope",
        "shapes/plot-description/slope/shapes.ttl",
        "shapes/plot-description/slope/valid.ttl",
        "shapes/plot-description/slope/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-slope-type",
        "shapes/plot-description/slope-type/shapes.ttl",
        "shapes/plot-description/slope-type/valid.ttl",
        "shapes/plot-description/slope-type/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-aspect",
        "shapes/plot-description/aspect/shapes.ttl",
        "shapes/plot-description/aspect/valid.ttl",
        "shapes/plot-description/aspect/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-landform-pattern",
        "shapes/plot-description/landform-pattern/shapes.ttl",
        "shapes/plot-description/landform-pattern/valid.ttl",
        "shapes/plot-description/landform-pattern/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-landform-element",
        "shapes/plot-description/landform-element/shapes.ttl",
        "shapes/plot-description/landform-element/valid.ttl",
        "shapes/plot-description/landform-element/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-outcrop-lithology",
        "shapes/plot-description/outcrop-lithology/shapes.ttl",
        "shapes/plot-description/outcrop-lithology/valid.ttl",
        "shapes/plot-description/outcrop-lithology/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-surface-strew-lithology",
        "shapes/plot-description/surface-strew-lithology/shapes.ttl",
        "shapes/plot-description/surface-strew-lithology/valid.ttl",
        "shapes/plot-description/surface-strew-lithology/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-surface-strew-size",
        "shapes/plot-description/surface-strew-size/shapes.ttl",
        "shapes/plot-description/surface-strew-size/valid.ttl",
        "shapes/plot-description/surface-strew-size/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-climatic-condition",
        "shapes/plot-description/climatic-condition/shapes.ttl",
        "shapes/plot-description/climatic-condition/valid.ttl",
        "shapes/plot-description/climatic-condition/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-cover-class",
        "shapes/plot-description/cover-class/shapes.ttl",
        "shapes/plot-description/cover-class/valid.ttl",
        "shapes/plot-description/cover-class/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-disturbance",
        "shapes/plot-description/disturbance/shapes.ttl",
        "shapes/plot-description/disturbance/valid.ttl",
        "shapes/plot-description/disturbance/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-fire-history",
        "shapes/plot-description/fire-history/shapes.ttl",
        "shapes/plot-description/fire-history/valid.ttl",
        "shapes/plot-description/fire-history/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-growth-form",
        "shapes/plot-description/growth-form/shapes.ttl",
        "shapes/plot-description/growth-form/valid.ttl",
        "shapes/plot-description/growth-form/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-growth-stage",
        "shapes/plot-description/growth-stage/shapes.ttl",
        "shapes/plot-description/growth-stage/valid.ttl",
        "shapes/plot-description/growth-stage/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-height-class",
        "shapes/plot-description/height-class/shapes.ttl",
        "shapes/plot-description/height-class/valid.ttl",
        "shapes/plot-description/height-class/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-most-dominant-species",
        "shapes/plot-description/most-dominant-species/shapes.ttl",
        "shapes/plot-description/most-dominant-species/valid.ttl",
        "shapes/plot-description/most-dominant-species/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-second-most-dominant-species",
        "shapes/plot-description/second-most-dominant-species/shapes.ttl",
        "shapes/plot-description/second-most-dominant-species/valid.ttl",
        "shapes/plot-description/second-most-dominant-species/invalid.ttl",
        7,
    ).astuple(),
    TestCaseItem(
        "plot-description-second-structural-formation",
        "shapes/plot-description/structural-formation/shapes.ttl",
        "shapes/plot-description/structural-formation/valid.ttl",
        "shapes/plot-description/structural-formation/invalid.ttl",
        7,
    ).astuple(),
]
