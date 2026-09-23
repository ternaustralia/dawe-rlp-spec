"""Generate a Shapes Graph, sg.ttl, per protocol and a top-level Shapes Graph in shapes/."""

import argparse
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, OWL, RDF, RDFS, URIRef, XSD, SH, SDO

TERN = URIRef("https://linked.data.gov.au/org/tern")


def write_shapes_graph(folder, modified, imports=None):
    """Write a protocol graph, or an import graph when imports is provided."""
    name = folder.name.replace("-", " ").replace("_", " ").strip().title()
    subject = URIRef(f"https://linked.data.gov.au/def/nrm/{folder.name}")
    graph = Graph()
    graph.bind("sh", SH)
    graph.bind("schema", SDO)
    graph.bind("xsd", XSD)
    for predicate, value in (
        (RDF.type, SH.ShapesGraph),
        (SDO.name, Literal(f"{name} Shapes Graph")),
        (SDO.description, Literal(f"SHACL Shapes Graph containing shapes for {name} protocol")),
        (SDO.dateCreated, Literal("2026-09-21", datatype=XSD.date)),
        (SDO.dateModified, Literal(modified, datatype=XSD.date)),
        (SDO.creator, TERN),
        (SDO.publisher, TERN),
        (SDO.codeRepository, Literal("https://github.com/ternaustralia/dawe-rlp-spec", datatype=XSD.anyURI)),
        (SDO.license, URIRef("http://purl.org/NET/rdflicense/cc-by4.0")),
    ):
        graph.add((subject, predicate, value))
    if imports is None:
        source = folder / "shapes.ttl"
        if source.is_file():
            shapes_graph = Graph().parse(source, format="turtle")
            for prefix, namespace in shapes_graph.namespaces():
                graph.bind(prefix, namespace)
            graph += shapes_graph
            shapes = set(shapes_graph.subjects(RDF.type, SH.NodeShape))
            shapes.update(shapes_graph.subjects(RDF.type, SH.PropertyShape))
            for shape in shapes:
                graph.add((shape, RDFS.isDefinedBy, subject))
                graph.add((subject, RDFS.member, shape))
            graph.bind("rdfs", RDFS)
        else:
            print(f"No {source}; generating metadata only")
    else:
        graph.bind("owl", OWL)
        for imported_graph in imports:
            graph.add((subject, OWL.imports, imported_graph))
    output = folder / "sg.ttl"
    graph.serialize(destination=output, format="longturtle")
    print(f"Created {output}")
    return subject


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_folder", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent / "shapes")
    args = parser.parse_args()
    if not args.root_folder.is_dir():
        parser.error(f"{args.root_folder} is not a directory")
    modified = date.today().isoformat()
    root_folder = args.root_folder.resolve()
    imports = []
    for folder in sorted(root_folder.iterdir()):
        if folder.is_dir():
            imports.append(write_shapes_graph(folder, modified))
    write_shapes_graph(root_folder, modified, imports=imports)


if __name__ == "__main__":
    main()
