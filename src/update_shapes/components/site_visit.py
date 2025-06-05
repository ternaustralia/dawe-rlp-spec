from rdflib import URIRef, SH, Graph, Literal, XSD
from settings import TERN
from common import add_common_properties, generate_target_bnode, generate_example_files_node, link_shapes_file
import string
from queries import get_protocol_label, query_to_get_observation_general_info

def generate_site_visit_shapes(op_collection_folder_path, op_shapes_folder_path, op_uri, protocol_uri):
    # Add common SHACL shapes properties
    g = Graph()
    uri = URIRef(
        "urn:shapes:"
        + op_collection_folder_path
        + ":"
        + op_shapes_folder_path
        + ":site-visit"
    )
    g = add_common_properties(g, uri)

    # Add SHACL shape description
    description = Literal(
        "Observations following the "
        + get_protocol_label(protocol_uri)
        + " are made in the context of a site visit."
    )
    g.add(
        (uri, SH.description, description)
    )

    # Add cardinality constraints
    g.add((uri, SH.maxCount, Literal(1)))
    g.add((uri, SH.minCount, Literal(1)))

    # Add SHACL shape messgae
    message = Literal("Observations _MUST_ have a value for `tern:hasSiteVisit`.")
    g.add((uri, SH.message, message))

    # Add SHACL shape name
    g.add((uri, SH.name, Literal("Site visit")))

    # Specify the SHACL shape path
    g.add((uri, SH.path, TERN.hasSiteVisit))

    # Add target blank node with query to get general info of the observation
    g = generate_target_bnode(g, uri, query_to_get_observation_general_info(op_uri))

    # Add valid and invalid files link in example ndoe
    g = generate_example_files_node(g, uri, op_collection_folder_path, op_shapes_folder_path)

    # Add link of SHACL shapes file
    g = link_shapes_file(g, uri, op_collection_folder_path, op_shapes_folder_path)

    return g