from pathlib import Path
from dataclasses import dataclass
from typing import List
import logging

from urlpath import URL
from rdflib import DCTERMS, Graph, URIRef, SH, Namespace

from src.asciidoc.templates import index_requirement_template, requirement_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WORKSPACE = "dawe-rlp-spec"
shapes_root_path = Path("/workspaces") / WORKSPACE / "shapes"
target_requirements_path = (
    Path("/workspaces") / WORKSPACE / "docs/source/requirements-by-module"
)
github_shapes_path = URL("https://github.com/ternaustralia/dawe-rlp-spec/blob/main")

REG = Namespace("http://purl.org/linked-data/registry#")


@dataclass
class Validator:
    url: str
    label: str


@dataclass
class Example:
    valid_url: str
    valid_label: str
    invalid_url: str
    invalid_label: str


@dataclass
class Requirement:
    iri: str
    label: str
    definition: str
    comment: str
    status: str
    conformance_classes: str
    source: str
    validators: List[Validator]
    examples: Example


def get_source_shapes_paths():
    """Get source shapes paths

    Only gets directories and ignores directories prefixed with underscore.
    """
    protocol_modules_shapes_paths = [
        m for m in shapes_root_path.iterdir() if m.is_dir() and m.name[0] != "_"
    ]
    return protocol_modules_shapes_paths


def get_source_requirements_sets(protocol_module_path: Path):
    return [
        requirement_set_path
        for requirement_set_path in protocol_module_path.iterdir()
        if requirement_set_path.is_dir()
    ]


# pylint: disable=invalid-name
def get_requirement(iri: URIRef, g: Graph) -> Requirement:
    label = g.value(iri, SH.name)
    definition = g.value(iri, SH.message)
    comment = g.value(iri, SH.description)
    status = str(g.value(iri, REG.status))
    conformance_classes = "`TBA`"  # TODO: Determine how to query this.
    source = g.value(iri, DCTERMS.source)
    validators = list(g.objects(iri, URIRef("urn:property:validators")))
    example_valid_url = None
    example_valid_label = None
    example_invalid_url = None
    example_invalid_label = None

    examples = g.value(iri, URIRef("urn:property:examples"))
    example_valid_url = g.value(examples, URIRef("urn:property:validExample"))
    example_valid_label = example_valid_url.split(str(github_shapes_path))[-1]
    example_invalid_url = g.value(examples, URIRef("urn:property:invalidExample"))
    example_invalid_label = example_invalid_url.split(str(github_shapes_path))[-1]

    requirement = Requirement(
        iri=iri,
        label=label,
        definition=definition,
        comment=comment,
        status=status,
        conformance_classes=conformance_classes,
        source=source,
        # v.split(str(github_shapes_path)[-1])
        validators=[
            Validator(url=v, label=v.split(str(github_shapes_path))[-1])
            for v in validators
        ],
        examples=Example(
            valid_url=example_valid_url,
            valid_label=example_valid_label,
            invalid_url=example_invalid_url,
            invalid_label=example_invalid_label,
        ),
    )

    return requirement


def generate_requirements():
    source_shapes_paths = get_source_shapes_paths()

    # For each protocol module wth shapes, loop through each observable property directory.
    # Each directory has a `shapes.ttl`, `valid.ttl` and `invalid.ttl` file.
    # Save the path of these files and

    print(source_shapes_paths)

    for source_protocol_module in source_shapes_paths:
        source_requirements_sets = get_source_requirements_sets(source_protocol_module)

        # Now that we have the requirement set's paths, we can loop through each one and
        # read the shape files.
        # For each requirement we find, we need to create a corresponding file in
        # the `target_requirements_path` in the form `<name>_<local-name-of-uri>.adoc`.
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
                    ?id a <urn:class:Requirement> .
                } ORDER BY ?id
            """
            )

            requirements: List[URIRef] = [result["id"] for result in results]

            # Used later to create the index.adoc file.
            asciidoc_files = []

            for req in requirements:
                # Create or overwrite asciidoc file with templated content.
                requirement_set_name = target_requirement_set.name
                local_name = req.split(":")[-1]
                asciidoc_file = (
                    target_requirement_set / f"{requirement_set_name}_{local_name}.adoc"
                )
                asciidoc_files.append(asciidoc_file.name)

                requirement = get_requirement(req, g)
                requirement_ascii = requirement_template.render(
                    local_name=f"{requirement_set_name}_{local_name}",
                    req=requirement,
                )

                logger.info("Writing ascii to %s", asciidoc_file.absolute())
                asciidoc_file.write_text(requirement_ascii)

            # Check if an index.adoc file exists, if not, create it and add an ascii
            # level 5 title with the "<name> Observation".
            # Capitalise the first letter in <name>.
            # If the file exists, insert an include directive
            # `include::<name>_<local-name-of-uri>.adoc[]`.
            asciidoc_index_file = target_requirement_set / "index.adoc"
            asciidoc_content = index_requirement_template.render(
                title=f"{module_name.capitalize()} Observation", files=asciidoc_files
            )
            asciidoc_index_file.write_text(asciidoc_content)
