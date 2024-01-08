from rdflib import URIRef, SH, Graph, Literal, SOSA
from settings import TERN
from common import add_common_properties, generate_target_bnode, generate_example_files_node, link_shapes_file
import string
from queries import query_to_get_observation_general_info

def generate_used_procedure_shapes(op_collection_folder_path, op_shapes_folder_path, protocol_label, protocol_uri, op_uri):
    # Add common SHACL shapes properties
    g = Graph()
    uri = URIRef(
        "urn:shapes:"
        + op_collection_folder_path
        + ":"
        + op_shapes_folder_path
        + ":used-procedure"
    )
    g = add_common_properties(g, uri)

    # Add SHACL shape description
    
    description = """IRI of procedure _MUST_ have the value `$protocol_uri`.

    `$protocol_uri` is the IRI for "$protocol_label"."""

    description = string.Template(
        description
    ).substitute(
        protocol_uri=f"<{protocol_uri}>",
        protocol_label=f"{protocol_label}",
    )
    g.add(
        (uri, SH.description, description)
    )

    # Add feature type URI as SHACL value
    g.add(
        (uri, SH.hasValue, URIRef(protocol_uri))
    )

    # Add SHACL shape messgae
    message = Literal(
        "The observation's `sosa:usedProcedure` _MUST_ have the value `"
        + protocol_uri
        + "`."
    )
    g.add((uri, SH.message, message))

    # Add SHACL shape name
    g.add((uri, SH.name, Literal("Used procedure")))

    # Specify the SHACL shape path
    g.add((uri, SH.path, SOSA.usedProcedure))

    # Add target blank node with query to find OPs
    g = generate_target_bnode(g, uri, query_to_get_observation_general_info(op_uri))

    # Add valid and invalid files link in example ndoe
    g = generate_example_files_node(g, uri, op_collection_folder_path, op_shapes_folder_path)

    # Add link of SHACL shapes file
    g = link_shapes_file(g, uri, op_collection_folder_path, op_shapes_folder_path)

    return g