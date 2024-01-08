from rdflib import RDF, SH, DCTERMS, BNode, Literal, URIRef, XSD
from settings import URNP, URNC, source, REG

def add_common_properties(g, uri):
    g.add((uri, RDF.type, SH.PropertyShape))
    g.add((uri, RDF.type, URNC.Requirement))
    g.add((uri, DCTERMS.source, source))
    g.add((uri, REG.status, REG.statusSubmitted))

    return g

def generate_target_bnode(g, uri, query):
    target_bnode = BNode()
    g.add((uri, SH.target, target_bnode))
    g.add((target_bnode, RDF.type, SH.SPARQLTarget))
    g.add(
        (target_bnode, SH.select, Literal(query))
    )

    return g


def generate_sparql_bnode(g, uri, query):
    sparql_bnode = BNode()
    g.add((uri, SH.sparql, sparql_bnode))
    g.add(
        (sparql_bnode, SH.select, Literal(query))
    )

    return g


def generate_example_files_node(g, uri, op_collection_folder_path, op_shapes_folder_path):
    
    invalid_examples_link = Literal(
        "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes/"
        + op_collection_folder_path
        + "/"
        + op_shapes_folder_path
        + "/invalid.ttl",
        datatype=XSD.anyURI,
    )

    valid_examples_link = Literal(
        "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes/"
        + op_collection_folder_path
        + "/"
        + op_shapes_folder_path
        + "/valid.ttl",
        datatype=XSD.anyURI,
    )
    
    example_files_node_uri = URIRef(
        "urn:shapes:" + op_collection_folder_path + ":" + op_shapes_folder_path + ":examples"
    )

    g.add((uri, URNP.examples, example_files_node_uri))
    g.add(
        (example_files_node_uri, URNP.invalidExample, invalid_examples_link)
    )
    g.add((example_files_node_uri, URNP.validExample, valid_examples_link))

    return g

def link_shapes_file (g, uri, op_collection_folder_path, op_shapes_folder_path):
    shapes_link = Literal(
        "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes/"
        + op_collection_folder_path
        + "/"
        + op_shapes_folder_path
        + "/shapes.ttl",
        datatype=XSD.anyURI,
    )

    g.add((uri, URNP.validator, shapes_link))

    return g