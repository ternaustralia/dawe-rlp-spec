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
]
