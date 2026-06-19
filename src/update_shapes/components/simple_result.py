from rdflib import URIRef, SH, Graph, Literal
from settings import TERN
from common import add_common_properties, generate_example_files_node, link_shapes_file, generate_sparql_bnode

def generate_simple_result_shapes(op_collection_folder_path, op_shapes_folder_path, op_uri):
    # Add common SHACL shapes properties
    g = Graph()
    uri = URIRef(
        "urn:shapes:"
        + op_collection_folder_path
        + ":"
        + op_shapes_folder_path
        + ":simple-result"
    )
    g = add_common_properties(g, uri)

    # Add SHACL shape description
    description = Literal("Value of `sosa:hasSimpleResult` _MUST_ be the same as the value in `sosa:hasResult`.")
    g.add(
        (uri, SH.description, description)
    )

    # Add SHACL shape messgae
    message = Literal(
        "The observation's `sosa:hasSimpleResult` _MUST_ have a value that is the same as the value in the value node of `sosa:hasResult`."
    )
    g.add((uri, SH.message, message))

    # Add SHACL shape name
    g.add((uri, SH.name, Literal("Simple result")))

    # Add SHACL SPARQL constraint to check the 2 values are the same
    q_shapes_get_simple_result_string1 = """
    PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select $this {
        $this a tern:Observation ;
            sosa:observedProperty 
    """
    q_shapes_get_simple_result_string2 = f"<{op_uri}>"
    q_shapes_get_simple_result_string3 = """
     ;
            sosa:hasSimpleResult ?simple ;
            sosa:hasResult ?result .
        ?result rdf:value ?value .
        filter (?simple != ?value)
    }
    """
    q_shapes_get_simple_result = (
        q_shapes_get_simple_result_string1
        + q_shapes_get_simple_result_string2
        + q_shapes_get_simple_result_string3
    )

    g = generate_sparql_bnode(g, uri, q_shapes_get_simple_result)

    # Add SHACL target class
    g.add((uri, SH.targetClass, TERN.Observation))

    # Add valid and invalid files link in example ndoe
    g = generate_example_files_node(g, uri, op_collection_folder_path, op_shapes_folder_path)

    # Add link of SHACL shapes file
    g = link_shapes_file(g, uri, op_collection_folder_path, op_shapes_folder_path)
    
    return g

