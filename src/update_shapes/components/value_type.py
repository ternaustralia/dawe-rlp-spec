from rdflib import URIRef, SH, Graph, Literal, SOSA
from common import add_common_properties, generate_target_bnode, generate_example_files_node, link_shapes_file
from queries import query_to_get_observation_general_info

def generate_value_type_shapes(op_collection_folder_path, op_shapes_folder_path, value_type_uri, op_uri):
    # Add common SHACL shapes properties
    g = Graph()
    uri = URIRef(
        "urn:shapes:"
        + op_collection_folder_path
        + ":"
        + op_shapes_folder_path
        + ":value-type"
    )
    g = add_common_properties(g, uri)

    # Add the SHACL class
    g.add((uri, SH["class"], URIRef(value_type_uri)))

    # Add SHACL shape description
    value_type_label = "tern:" + value_type_uri.split("/")[-1]
    description = Literal(
        "The value of `sosa:hasResult` _MUST_ be a `" + value_type_label + "`."
    )
    g.add(
        (uri, SH.description, description)
    )

    # Add SHACL shape messgae
    message = Literal(
        "The result _MUST_ be an instance of `" + value_type_label + "`."
    )
    g.add((uri, SH.message, message))

    # Add SHACL shape name
    g.add((uri, SH.name, Literal("Value type")))

    # Specify the SHACL shape path
    g.add((uri, SH.path, SOSA.hasResult))

    # Add target blank node with query to find general info of the observation
    g = generate_target_bnode(g, uri, query_to_get_observation_general_info(op_uri))

    # Add valid and invalid files link in example ndoe
    g = generate_example_files_node(g, uri, op_collection_folder_path, op_shapes_folder_path)

    # Add link of SHACL shapes file
    g = link_shapes_file(g, uri, op_collection_folder_path, op_shapes_folder_path)

    return g