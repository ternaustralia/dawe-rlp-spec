from rdflib import RDF, SH, DCTERMS, BNode, Literal, URIRef, XSD, SOSA
from settings import (
    URNP,
    URNC,
    source,
    REG,
    dataset_example,
    phenomenon_time_example,
    result_time_example,
    sitevisit_example,
)
from functions import (
    generate_op_shapes_folder,
    generate_protocol_folder,
    generate_observation_comment,
)


def add_common_properties_shapes(g, uri):
    g.add((uri, RDF.type, SH.PropertyShape))
    g.add((uri, RDF.type, URNC.Requirement))
    g.add((uri, DCTERMS.source, source))
    g.add((uri, REG.status, REG.statusSubmitted))

    return g


def generate_target_bnode(g, uri, query):
    target_bnode = BNode()
    g.add((uri, SH.target, target_bnode))
    g.add((target_bnode, RDF.type, SH.SPARQLTarget))
    g.add((target_bnode, SH.select, Literal(query)))

    return g


def generate_sparql_bnode(g, uri, query):
    sparql_bnode = BNode()
    g.add((uri, SH.sparql, sparql_bnode))
    g.add((sparql_bnode, SH.select, Literal(query)))

    return g


def generate_example_files_node(
    g, uri, op_collection_folder_path, op_shapes_folder_path
):

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
        "urn:shapes:"
        + op_collection_folder_path
        + ":"
        + op_shapes_folder_path
        + ":examples"
    )

    g.add((uri, URNP.examples, example_files_node_uri))
    g.add((example_files_node_uri, URNP.invalidExample, invalid_examples_link))
    g.add((example_files_node_uri, URNP.validExample, valid_examples_link))

    return g


def link_shapes_file(g, uri, op_collection_folder_path, op_shapes_folder_path):
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


# This function will add observation example nodes for both invalid and valid examples
def add_observation_examples(
    g,
    validation_type,
    protocol_label,
    op_label,
    example_type,
    data_type,
    value_type,
    feature_type,
    example_value,
    op_uri,
    protocol_uri,
):
    # Generate the Observation URI
    uri = URIRef(
        "urn:test:"
        + generate_protocol_folder(protocol_label)
        + generate_op_shapes_folder(op_label)
        + ":"
        + validation_type
        + ":"
        + example_type
    )

    # Generate the Observation comment
    comment = Literal(
        generate_observation_comment(
            validation_type,
            example_type,
            data_type,
            protocol_label,
            value_type,
            op_label,
        )
    )

    g.add((uri, RDF.type, TERN.Observation))
    g.add((uri, VOID.inDataset, dataset_example))
    g.add((uri, RDFS.comment, comment))

    # Generate the feature of interest node
    foi_bnode = BNode()
    g.add(
        (
            uri,
            SOSA.hasFeatureOfInterest,
            foi_bnode,
        )
    )
    g.add(
        (
            foi_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    g.add(
        (
            foi_bnode,
            VOID.inDataset,
            dataset_example,
        )
    )

    # Add invalid example of feature type if the example is for feature type, other wise add the valid one
    if validation_type == "invalid" and example_type == "featuretype":
        feature_type_value = URIRef("urn:fake:feature-type")
    else:
        feature_type_value == URIRef(feature_type)

    g.add(
        (
            foi_bnode,
            TERN.featureType,
            feature_type_value,
        )
    )

    # Add generate content of the result node and the observation example
    result_node = BNode()
    g.add((uri, SOSA.hasResult, result_node))
    g.add((result_node, RDF.type, TERN.Value))
    g.add((result_node, SOSA.isResultOf, uri))
    g.add((uri, SOSA.observedProperty, URIRef(op_uri)))
    g.add((uri, SOSA.phenomenonTime, phenomenon_time_example))
    g.add((uri, SOSA.resultTime, result_time_example))

    # Add invalid example of used procedure if the example is for used procedure, other wise add the valid one
    if validation_type == "invalid" and example_type == "usedprocedure":
        used_procedure_value = URIRef("urn:fake:used-procedure")
    else:
        used_procedure_value == URIRef(protocol_uri)

    g.add((uri, SOSA.usedProcedure, used_procedure_value))

    # TODO: Add site visit if it's not `Opportune` or `Vegetation Mapping`
    g.add((uri, TERN.hasSiteVisit, sitevisit_example))
