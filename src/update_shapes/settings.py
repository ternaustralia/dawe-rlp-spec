from rdflib import Namespace, Literal

URNC = Namespace("urn:class:")
URNP = Namespace("urn:property:")
REG = Namespace("http://purl.org/linked-data/registry#")
TERN = Namespace("https://w3id.org/tern/ontologies/tern/")
UNIT = Namespace("http://qudt.org/vocab/unit/")

dawe_endpoint = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core"
tern_endpoint = "https://graphdb.tern.org.au/repositories/tern_vocabs_core"

source = Literal("Ecological Monitoring System Australia (EMSA) Protocols")