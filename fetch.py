from rdflib.namespace import RDF, RDFS, VOID, XSD, SOSA, DCTERMS, PROV, TIME
from rdflib import Graph, Namespace, URIRef, Literal, BNode

g = Graph()

SHACL = Namespace("http://www.w3.org/ns/shacl#")
g.bind("sh", SHACL)

g.parse("shapes/plot-description/slope-type/shapes_original.ttl")

q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        select ?values {
            service <https://graphdb.tern.org.au/repositories/dawe_vocabs_core> {
                ?s skos:prefLabel ?label ;
                   skos:member ?values .
                filter (?label = "Plot slope codes")
            }
        }
"""

start_from_the_last_blank_node = True
for r in g.query(q):
    node_value = BNode()
    g.add((node_value, SHACL.path, RDF.value))
    g.add((node_value, SHACL.hasValue, r["values"]))
    node_property = BNode()
    g.add((node_property, SHACL.property, node_value))

    if start_from_the_last_blank_node:
        lastNode = BNode()
        g.add((lastNode, RDF.first, node_property))
        g.add((lastNode, RDF.rest, RDF.nil))
        start_from_the_last_blank_node = False
    else:
        nextNode = BNode()
        g.add((nextNode, RDF.first, node_property))
        g.add((nextNode, RDF.rest, lastNode))
        lastNode = nextNode

g.add(
    (
        URIRef("urn:shapes:plot-description:slope-type:result-category"),
        SHACL.xone,
        lastNode,
    )
)


g.serialize("shapes/plot-description/slope-type/shapes.ttl")
