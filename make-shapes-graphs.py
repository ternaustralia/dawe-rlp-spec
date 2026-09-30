"""Generate sg.ttl for every directory containing uuid.txt under shapes/.

Files are only rewritten when their content changes.
"""

import argparse
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef, XSD, SH, SDO
from rdflib.compare import isomorphic

TERN = URIRef("https://linked.data.gov.au/org/tern")
NRMV = Namespace("https://linked.data.gov.au/def/nrm/validator/")
SHAPES_GRAPH = URIRef(f"{SH}ShapesGraph")
TOP_LEVEL_NAME = "Ecological Monitoring System - Australia Field Survey Protocols Shapes Graph"
TOP_LEVEL_DESCRIPTION = ("SHACL Shapes Graph containing all the module and protocol Shapes Graphs "
                         "of the Ecological Monitoring System - Australia Field Survey Protocols")


def graph_iri(folder):
    return NRMV[(folder / "uuid.txt").read_text().strip()]


def find_source(folder, subject):
    """Return (shapes graph, self_described). A self-described file declares its own Shapes Graph."""
    source = folder / "shapes.ttl"
    if source.is_file():
        return Graph().parse(source, format="turtle"), False
    for candidate in sorted(folder.glob("*shapes.ttl")):
        graph = Graph().parse(candidate, format="turtle")
        if (subject, RDF.type, SHAPES_GRAPH) in graph:
            return graph, True
    return None, False


def build_shapes_graph(folder, imports=None, *, top_level=False):
    """Return (graph, subject, self_described), without schema:dateModified."""
    subject = graph_iri(folder)
    source, self_described = (None, False) if imports is not None else find_source(folder, subject)
    if self_described:
        return source, subject, True

    name = folder.name.replace("-", " ").replace("_", " ").strip().title()
    display_name = folder.name.replace("shapes", "").replace("-", " ").replace("_", " ")
    display_name = " ".join(display_name.split()).title()
    kind = "protocol" if folder.name.endswith("-protocol-shapes") else "module"
    graph = Graph()
    graph.bind("sh", SH)
    graph.bind("schema", SDO)
    graph.bind("xsd", XSD)
    for predicate, value in (
        (RDF.type, SHAPES_GRAPH),
        (SDO.name, Literal(TOP_LEVEL_NAME if top_level else f"{display_name} Shapes Graph")),
        (SDO.description, Literal(TOP_LEVEL_DESCRIPTION if top_level
                                  else f"SHACL Shapes Graph containing shapes for {name} {kind}")),
        (SDO.dateCreated, Literal("2026-09-21", datatype=XSD.date)),
        (SDO.creator, TERN),
        (SDO.publisher, TERN),
        (SDO.codeRepository, Literal("https://github.com/ternaustralia/dawe-rlp-spec", datatype=XSD.anyURI)),
        (SDO.license, URIRef("http://purl.org/NET/rdflicense/cc-by4.0")),
    ):
        graph.add((subject, predicate, value))
    if imports is not None:
        graph.bind("owl", OWL)
        for imported_graph in imports:
            graph.add((subject, OWL.imports, imported_graph))
    elif source is not None:
        for prefix, namespace in source.namespaces():
            graph.bind(prefix, namespace)
        graph += source
        shapes = set(source.subjects(RDF.type, SH.NodeShape))
        shapes.update(source.subjects(RDF.type, SH.PropertyShape))
        for shape in shapes:
            graph.add((shape, RDFS.isDefinedBy, subject))
            graph.add((subject, RDFS.member, shape))
        graph.bind("rdfs", RDFS)
    return graph, subject, False


def build_all(root_folder):
    """Build every Shapes Graph under root_folder, keyed by folder."""
    folders = sorted({path.parent for path in root_folder.rglob("uuid.txt") if path.is_file()})
    graphs, imports = {}, []
    for folder in folders:
        if folder != root_folder:
            graphs[folder] = build_shapes_graph(folder)
            imports.append(graphs[folder][1])
    if root_folder in folders:
        graphs[root_folder] = build_shapes_graph(root_folder, imports=imports, top_level=True)
    return graphs


def signature(graph, ignore=(SDO.dateModified,)):
    """Fast canonical form for graphs with acyclic blank nodes; None if there is a cycle."""
    triples = [triple for triple in graph if triple[1] not in ignore]
    children, incoming = defaultdict(list), Counter()
    for s, p, o in triples:
        if isinstance(s, BNode):
            children[s].append((p, o))
        if isinstance(o, BNode):
            incoming[o] += 1
    canonical = {}
    for start in {t for triple in triples for t in (triple[0], triple[2]) if isinstance(t, BNode)}:
        if start in canonical:
            continue
        stack, on_stack = [start], {start}
        while stack:
            node = stack[-1]
            pending = list(dict.fromkeys(o for _, o in children.get(node, ()) if isinstance(o, BNode) and o not in canonical))
            if pending:
                if on_stack.intersection(pending):
                    return None
                stack.extend(pending)
                on_stack.update(pending)
                continue
            canonical[node] = "[" + " ; ".join(sorted(
                f"{p.n3()} {canonical[o] if isinstance(o, BNode) else o.n3()}" for p, o in children.get(node, ())
            )) + "]"
            stack.pop()
            on_stack.discard(node)
    term = lambda t: canonical[t] if isinstance(t, BNode) else t.n3()
    lines = sorted(f"{term(s)} {p.n3()} {term(o)}" for s, p, o in triples
                   if not isinstance(s, BNode) or not incoming[s])
    # Counting blank nodes per content catches a shared blank node being split into copies.
    return lines, sorted(Counter(canonical.values()).items())


def same_content(first, second):
    """True if the graphs are equal, ignoring schema:dateModified."""
    first_signature, second_signature = signature(first), signature(second)
    if first_signature is not None and second_signature is not None:
        return first_signature == second_signature
    def strip(graph):
        stripped = Graph()
        for triple in graph:
            if triple[1] != SDO.dateModified:
                stripped.add(triple)
        return stripped
    return isomorphic(strip(first), strip(second))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_folder", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent / "shapes")
    args = parser.parse_args()
    if not args.root_folder.is_dir():
        parser.error(f"{args.root_folder} is not a directory")
    modified = date.today().isoformat()
    updated = 0
    for folder, (graph, subject, self_described) in build_all(args.root_folder.resolve()).items():
        output = folder / "sg.ttl"
        if output.is_file() and same_content(graph, Graph().parse(output, format="turtle")):
            continue
        updated += 1
        if not self_described:
            graph.add((subject, SDO.dateModified, Literal(modified, datatype=XSD.date)))
        output.write_text(graph.serialize(format="longturtle").rstrip("\n") + "\n")
        print(f"Updated {output}")
    print(f"{updated} sg.ttl files updated")


if __name__ == "__main__":
    main()
