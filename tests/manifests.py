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
        name="plot-description-structural-formation",
        shapes_path="shapes/plot-description/structural-formation/shapes.ttl",
        valid_data_path="shapes/plot-description/structural-formation/valid.ttl",
        invalid_data_path="shapes/plot-description/structural-formation/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-slope-class",
        shapes_path="shapes/plot-description/slope-class/shapes.ttl",
        valid_data_path="shapes/plot-description/slope-class/valid.ttl",
        invalid_data_path="shapes/plot-description/slope-class/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-height-class",
        shapes_path="shapes/plot-description/height-class/shapes.ttl",
        valid_data_path="shapes/plot-description/height-class/valid.ttl",
        invalid_data_path="shapes/plot-description/height-class/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-homogeneity-measure",
        shapes_path="shapes/plot-description/homogeneity-measure/shapes.ttl",
        valid_data_path="shapes/plot-description/homogeneity-measure/valid.ttl",
        invalid_data_path="shapes/plot-description/homogeneity-measure/invalid.ttl",
        expected_failures=8,
    ),
    TestCaseItem(
        name="plot-description-surface-strew-size",
        shapes_path="shapes/plot-description/surface-strew-size/shapes.ttl",
        valid_data_path="shapes/plot-description/surface-strew-size/valid.ttl",
        invalid_data_path="shapes/plot-description/surface-strew-size/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-landform-pattern",
        shapes_path="shapes/plot-description/landform-pattern/shapes.ttl",
        valid_data_path="shapes/plot-description/landform-pattern/valid.ttl",
        invalid_data_path="shapes/plot-description/landform-pattern/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-rock-outcrop-lithology",
        shapes_path="shapes/plot-description/rock-outcrop-lithology/shapes.ttl",
        valid_data_path="shapes/plot-description/rock-outcrop-lithology/valid.ttl",
        invalid_data_path="shapes/plot-description/rock-outcrop-lithology/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-cover",
        shapes_path="shapes/plot-description/cover/shapes.ttl",
        valid_data_path="shapes/plot-description/cover/valid.ttl",
        invalid_data_path="shapes/plot-description/cover/invalid.ttl",
        expected_failures=8,
    ),
    TestCaseItem(
        name="plot-description-disturbance-type",
        shapes_path="shapes/plot-description/disturbance-type/shapes.ttl",
        valid_data_path="shapes/plot-description/disturbance-type/valid.ttl",
        invalid_data_path="shapes/plot-description/disturbance-type/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-surface-strew-lithology",
        shapes_path="shapes/plot-description/surface-strew-lithology/shapes.ttl",
        valid_data_path="shapes/plot-description/surface-strew-lithology/valid.ttl",
        invalid_data_path="shapes/plot-description/surface-strew-lithology/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-second-dominant-species",
        shapes_path="shapes/plot-description/second-dominant-species/shapes.ttl",
        valid_data_path="shapes/plot-description/second-dominant-species/valid.ttl",
        invalid_data_path="shapes/plot-description/second-dominant-species/invalid.ttl",
        expected_failures=6,
    ),
    TestCaseItem(
        name="plot-description-landform-element",
        shapes_path="shapes/plot-description/landform-element/shapes.ttl",
        valid_data_path="shapes/plot-description/landform-element/valid.ttl",
        invalid_data_path="shapes/plot-description/landform-element/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-slope",
        shapes_path="shapes/plot-description/slope/shapes.ttl",
        valid_data_path="shapes/plot-description/slope/valid.ttl",
        invalid_data_path="shapes/plot-description/slope/invalid.ttl",
        expected_failures=8,
    ),
    TestCaseItem(
        name="plot-description-fire-history",
        shapes_path="shapes/plot-description/fire-history/shapes.ttl",
        valid_data_path="shapes/plot-description/fire-history/valid.ttl",
        invalid_data_path="shapes/plot-description/fire-history/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-growth-form",
        shapes_path="shapes/plot-description/growth-form/shapes.ttl",
        valid_data_path="shapes/plot-description/growth-form/valid.ttl",
        invalid_data_path="shapes/plot-description/growth-form/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-climatic-condition",
        shapes_path="shapes/plot-description/climatic-condition/shapes.ttl",
        valid_data_path="shapes/plot-description/climatic-condition/valid.ttl",
        invalid_data_path="shapes/plot-description/climatic-condition/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-growth-stage",
        shapes_path="shapes/plot-description/growth-stage/shapes.ttl",
        valid_data_path="shapes/plot-description/growth-stage/valid.ttl",
        invalid_data_path="shapes/plot-description/growth-stage/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-third-dominant-species",
        shapes_path="shapes/plot-description/third-dominant-species/shapes.ttl",
        valid_data_path="shapes/plot-description/third-dominant-species/valid.ttl",
        invalid_data_path="shapes/plot-description/third-dominant-species/invalid.ttl",
        expected_failures=6,
    ),
    TestCaseItem(
        name="plot-description-aspect",
        shapes_path="shapes/plot-description/aspect/shapes.ttl",
        valid_data_path="shapes/plot-description/aspect/valid.ttl",
        invalid_data_path="shapes/plot-description/aspect/invalid.ttl",
        expected_failures=8,
    ),
    TestCaseItem(
        name="plot-description-cover-class",
        shapes_path="shapes/plot-description/cover-class/shapes.ttl",
        valid_data_path="shapes/plot-description/cover-class/valid.ttl",
        invalid_data_path="shapes/plot-description/cover-class/invalid.ttl",
        expected_failures=7,
    ),
    TestCaseItem(
        name="plot-description-dominant-species",
        shapes_path="shapes/plot-description/dominant-species/shapes.ttl",
        valid_data_path="shapes/plot-description/dominant-species/valid.ttl",
        invalid_data_path="shapes/plot-description/dominant-species/invalid.ttl",
        expected_failures=6,
    ),
]
