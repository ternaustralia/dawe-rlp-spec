from pathlib import Path
from dataclasses import dataclass

from urlpath import URL
from rdflib import Graph

from src.asciidoc.templates import index_requirement_template

WORKSPACE = "dawe-rlp-spec"
shapes_root_path = Path("/workspaces") / WORKSPACE / "shapes"
target_requirements_path = (
    Path("/workspaces") / WORKSPACE / "docs/source/requirements-by-module"
)
github_shapes_path = URL(
    "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes"
)


@dataclass
class Requirement:
    iri: str
    label: str
    definition: str
    comment: str
    status: str
    conformance_classes: str
    source: str
    validators: str
    examples: str


def get_source_shapes_paths():
    protocol_modules_shapes_paths = [
        m for m in shapes_root_path.iterdir() if m.is_dir()
    ]
    return protocol_modules_shapes_paths


def get_source_requirements_sets(protocol_module_path: Path):
    return [
        requirement_set_path
        for requirement_set_path in protocol_module_path.iterdir()
        if requirement_set_path.is_dir()
    ]


def get_requirement(
    iri: str, shape_file: Path, valid_data_file: Path, invalid_data_file: Path
) -> Requirement:
    pass


def generate_requirements():
    source_shapes_paths = get_source_shapes_paths()

    # For each protocol module wth shapes, loop through each observable property directory.
    # Each directory has a `shapes.ttl`, `valid.ttl` and `invalid.ttl` file.
    # Save the path of these files and

    print(source_shapes_paths)

    for source_protocol_module in source_shapes_paths:
        source_requirements_sets = get_source_requirements_sets(source_protocol_module)

        # Now that we have the requirement set's paths, we can loop through each one and read the shape files.
        # For each requirement we find, we need to create a corresponding file in the `target_requirements_path` in
        # the form `<name>_<local-name-of-uri>.adoc`.
        for source_requirement_set in source_requirements_sets:
            module_name = source_requirement_set.name
            target_requirement_set = target_requirements_path / "/".join(
                source_requirement_set.parts[-2:]
            )

            # Get a list of requirements.
            # Loop through them.
            g = Graph()
            g.parse(str(source_requirement_set / "shapes.ttl"))

            results = g.query(
                """
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                
                SELECT ?id
                WHERE {
                    {
                        ?id a sh:PropertyShape .
                    }
                    UNION {
                        ?id a sh:NodeShape .
                    }
                } ORDER BY ?id
            """
            )
            requirements = [result["id"] for result in results]

            # Used later to create the index.adoc file.
            asciidoc_files = []

            for req in requirements:
                # Create or overwrite asciidoc file with templated content.
                requirement_set_name = target_requirement_set.name
                local_name = req.split(":")[-1]
                asciidoc_file = (
                    target_requirement_set
                    / f"{requirement_set_name}_{local_name}.adoc.test"  # TODO: Remove test suffix
                )
                asciidoc_files.append(asciidoc_file.name)

            # Check if an index.adoc file exists, if not, create it and add an ascii level 5 title with the "<name> Observation".
            # Capitalise the first letter in <name>.
            # If the file exists, insert an include directive `include::<name>_<local-name-of-uri>.adoc[]`.
            asciidoc_index_file = (
                target_requirement_set / "index.adoc.test"
            )  # TODO: Remove test suffix
            asciidoc_content = index_requirement_template.render(
                title=f"{module_name.capitalize()} Observation", files=asciidoc_files
            )
            asciidoc_index_file.write_text(asciidoc_content)
