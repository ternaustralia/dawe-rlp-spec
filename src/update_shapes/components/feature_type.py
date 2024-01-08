from rdflib import URIRef, SH, Graph, Literal
from settings import TERN
from common import add_common_properties, generate_target_bnode, generate_example_files_node, link_shapes_file
import string

def generate_feature_type_shapes(op_collection_folder_path, op_shapes_folder_path, feature_type_label, feature_type_uri, op_uri):
    # Add common SHACL shapes properties
    g = Graph()
    uri = URIRef(
        "urn:shapes:"
        + op_collection_folder_path
        + ":"
        + op_shapes_folder_path
        + ":feature-type"
    )
    g = add_common_properties(g, uri)

    # Add SHACL shape description
    description = Literal(
        "TERN's ecologists have determined the feature type is _"
        + feature_type_label
        + "_, defined by the link:https://www.publish.csiro.au/book/5230/[Australian Soil and Land Survey Field Handbook]."
    )
    g.add(
        (uri, SH.description, description)
    )

    # Add feature type URI as SHACL value
    g.add(
        (uri, SH.hasValue, URIRef(feature_type_uri))
    )

    # Add SHACL shape messgae
    message = Literal(
        "The value of `tern:featureType` _MUST_ be link: "
        + feature_type_uri
        + "[`"
        + feature_type_label
        + "`]."
    )
    g.add((uri, SH.message, message))

    # Add SHACL shape name
    g.add((uri, SH.name, Literal("Feature type")))

    # Specify the SHACL shape path
    g.add((uri, SH.path, TERN.featureType))

    # Add target blank node with query to find OPs
    q_shapes_get_foi = """
    PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    select ?this  {
        values ?op_uri {$op_uri}
        ?observation a tern:Observation ;
            sosa:observedProperty ?op_uri ;
            sosa:hasFeatureOfInterest ?this .
    }
    """

    q_shapes_get_foi = string.Template(q_shapes_get_foi).substitute(
        op_uri=f"<{op_uri}>"
    )
    g = generate_target_bnode(g, uri, q_shapes_get_foi)

    # Add valid and invalid files link in example ndoe
    g = generate_example_files_node(g, uri, op_collection_folder_path, op_shapes_folder_path)

    # Add link of SHACL shapes file
    g = link_shapes_file(g, uri, op_collection_folder_path, op_shapes_folder_path)

    return g