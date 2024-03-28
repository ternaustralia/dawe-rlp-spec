from rdflib import Namespace, Literal, URIRef, XSD

URNC = Namespace("urn:class:")
URNP = Namespace("urn:property:")
REG = Namespace("http://purl.org/linked-data/registry#")
TERN = Namespace("https://w3id.org/tern/ontologies/tern/")
UNIT = Namespace("http://qudt.org/vocab/unit/")

dawe_endpoint = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core"
tern_endpoint = "https://graphdb.tern.org.au/repositories/tern_vocabs_core"

source = Literal("Ecological Monitoring System Australia (EMSA) Protocols")
phenomenon_time_example = URIRef(
    "https://example.com/observation/examplePhenomenonTime"
)
result_time_example = Literal("2022-09-27T05:38:47.117000+00:00", datatype=XSD.dateTime)
dataset_example = URIRef("https://example.com/dataset/1")
sitevisit_example = URIRef("urn:test:sitevisit")
