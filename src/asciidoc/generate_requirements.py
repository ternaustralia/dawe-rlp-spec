from pathlib import Path
from dataclasses import dataclass
from typing import List
import logging
import requests
from requests.exceptions import HTTPError

from urlpath import URL
from rdflib import DCTERMS, Graph, URIRef, SH, Namespace, RDF
from rdflib.collection import Collection

from src.asciidoc.templates import (
    index_requirement_template,
    requirement_template,
    requirements_sections_template,
)
from src.asciidoc.sparql_templates import query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WORKSPACE = "dawe-rlp-spec"
shapes_root_path = Path("/workspaces") / WORKSPACE / "shapes"
target_requirements_path = (
    Path("/workspaces") / WORKSPACE / "docs/source/requirements-by-module"
)
requirements_sections_file = (
    Path("/workspaces") / WORKSPACE / "docs/source/requirements-sections.adoc"
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
    validator: Validator
    examples: Example


class SPARQLQueryError(Exception):
    pass


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
    validator = g.value(iri, URIRef("urn:property:validator"))
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
        validator=Validator(
            url=validator, label=validator.split(str(github_shapes_path))[-1]
        ),
        examples=Example(
            valid_url=example_valid_url,
            valid_label=example_valid_label,
            invalid_url=example_invalid_url,
            invalid_label=example_invalid_label,
        ),
    )

    return requirement


def sparql_query(url: str, query: str):
    headers = {
        "Content-type": "application/sparql-query",
        "Accept": "application/sparql-results+json",
    }
    r = requests.post(url, headers=headers, data=query)
    try:
        r.raise_for_status()
    except HTTPError as err:
        raise SPARQLQueryError(
            f"Failed fetching data from {url} SPARQL endpoint. Code: {r.status_code} Message: {r.text}."
        ) from err
    return r.json()


def get_controlled_iris(iri, g):
    values = g.value(iri, SH["in"])
    collection = Collection(g, values)

    return collection


def is_controlled(iri: URIRef, g: Graph) -> bool:
    for _, _, _ in g.triples((iri, RDF.type, URIRef("urn:class:Controlled"))):
        return True
    return False


def get_controlled_iris_and_labels(collection: Collection, sparql_endpoint: str, g: Graph):
    lst = list(collection.__iter__())
    errors = 0
    results = query.render(items=lst)
    iris_and_labels = []

    try:
        data = sparql_query(sparql_endpoint, results)
        for iri in data["results"]["bindings"]:
            iris_and_labels.append([str(iri["iri"]["value"]), str(iri["label"]["value"])])

    except SPARQLQueryError as err:
        logger.error(str(err))
        errors += 1

    if errors:
        logger.info(f"{errors} error occurred.")

    return iris_and_labels


def generate_requirements():
    source_shapes_paths = get_source_shapes_paths()

    # We use this later to build the requirements-sections.adoc file.
    requirements_sections = []

    # For each protocol module wth shapes, loop through each observable property directory.
    # Each directory has a `shapes.ttl`, `valid.ttl` and `invalid.ttl` file.
    # Save the path of these files and

    for source_protocol_module in source_shapes_paths:
        logger.info("Processing shapes in %s", source_protocol_module)
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

                if is_controlled(req, g):
                    controlled_iris = get_controlled_iris(req, g)
                    endpoint = g.value(req, URIRef("urn:property:sparqlEndpoint"))
                    iris_and_labels_list = get_controlled_iris_and_labels(controlled_iris, endpoint, g)
                    
                    requirement_ascii = requirement_template.render(
                        local_name=f"{requirement_set_name}_{local_name}",
                        req=requirement,
                        add_controlled=is_controlled(req, g),
                        table_values=iris_and_labels_list,
                    )
                    
                else:
                    requirement_ascii = requirement_template.render(
                        local_name=f"{requirement_set_name}_{local_name}",
                        req=requirement,
                    )

                logger.info("Writing ascii to %s", asciidoc_file.absolute())
                target_requirement_set.mkdir(exist_ok=True)
                asciidoc_file.write_text(requirement_ascii)

            # Check if an index.adoc file exists, if not, create it and add an ascii
            # level 5 title with the "<name> Observation".
            # Capitalise the first letter in <name>.
            # If the file exists, insert an include directive
            # `include::<name>_<local-name-of-uri>.adoc[]`.
            target_requirement_set.mkdir(exist_ok=True)
            asciidoc_index_file = target_requirement_set / "index.adoc"
            asciidoc_content = index_requirement_template.render(
                title=f"{module_name.capitalize().replace('-', ' ')} Observation",
                files=asciidoc_files,
            )
            asciidoc_index_file.write_text(asciidoc_content)
            requirements_sections.append(asciidoc_index_file)

    # Write to requirements-sections.adoc
    sections = [
        str(s).rsplit("/workspaces/dawe-rlp-spec/docs/source/", maxsplit=1)[-1]
        for s in requirements_sections
    ]
    sections_ascii = requirements_sections_template.render(sections=sections)
    requirements_sections_file.write_text(sections_ascii)
