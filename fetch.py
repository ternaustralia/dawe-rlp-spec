import logging
import typer
from rdflib.namespace import RDF, RDFS, VOID, XSD, SOSA, DCTERMS, PROV, TIME
from rdflib import Graph, Namespace, URIRef, Literal, BNode

app = typer.Typer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def fetch(filename: str):

    g = Graph()

    SHACL = Namespace("http://www.w3.org/ns/shacl#")
    g.bind("sh", SHACL)

    g.parse(filename)

    q_delete = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        delete {
            ?s sh:xone ?node .
            ?node rdf:rest ?item .
            ?item rdf:first ?head ;
                rdf:rest ?tail .
            ?head sh:property ?property .
            ?property sh:path rdf:value ;
            sh:hasValue ?value .
        }
        where {
            ?s sh:xone ?node .
            ?node rdf:rest* ?item .
            ?item rdf:first ?head ;
                rdf:rest ?tail .
            ?head sh:property ?property .
            ?property sh:path rdf:value ;
            sh:hasValue ?value .
        }
    """

    logger.info(f"Delete sh:xone in file '{filename}'")
    g.update(q_delete)

    q = """
        select ?uri ?query {
            ?uri a <urn:class:Controlled> ;
            <urn:property:query> ?query .
        }
    """

    for query in g.query(q).bindings:
        start_from_the_last_blank_node = True
        uri = query["uri"]
        logger.info(f"Updating sh:xone of shape '{uri}' in '{filename}'")
        for r in g.query(query["query"]):
            node_value = BNode()
            g.add((node_value, SHACL.path, RDF.value))
            g.add((node_value, SHACL.hasValue, r["values"]))
            node_property = BNode()
            g.add((node_property, SHACL.property, node_value))

            if start_from_the_last_blank_node:
                last_node = BNode()
                g.add((last_node, RDF.first, node_property))
                g.add((last_node, RDF.rest, RDF.nil))
                start_from_the_last_blank_node = False
            else:
                next_node = BNode()
                g.add((next_node, RDF.first, node_property))
                g.add((next_node, RDF.rest, last_node))
                last_node = next_node

        g.add(
            (
                uri,
                SHACL.xone,
                last_node,
            )
        )

        logger.info(f"Updated sh:xone of shape '{uri}' in '{filename}'")

    g.serialize(filename)


if __name__ == "__main__":
    app()
