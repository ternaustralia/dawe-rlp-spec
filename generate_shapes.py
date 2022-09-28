import pathlib
from pathlib import Path
import uuid
from typing import Collection, Literal

import rdflib
from rdflib import (
    DCTERMS,
    SKOS,
    Graph,
    Literal,
    Namespace,
    URIRef,
    SH,
    BNode,
    SOSA,
    VOID,
)
from rdflib.namespace import RDF, RDFS, SDO, SKOS, XSD

import requests
from requests.exceptions import HTTPError

import json

import string

URNC = Namespace("urn:class:")
URNP = Namespace("urn:property:")
REG = Namespace("http://purl.org/linked-data/registry#")
TERN = Namespace("https://w3id.org/tern/ontologies/tern/")


dawe_endpoint = "https://graphdb.tern.org.au/repositories/dawe_vocabs_core"
tern_endpoint = "https://graphdb.tern.org.au/repositories/tern_vocabs_core"

properties_collection_uri = (
    "https://linked.data.gov.au/def/test/dawe-cv/bc009349-c1d0-4000-a5d0-1b1c18c3ea0e"
)
protocol_module_uri = (
    "https://linked.data.gov.au/def/test/dawe-cv/576f634e-2706-4f18-b561-0636d4c007d0"
)

values_tbd = "values_tbd"

source = Literal("TERN Ecosystem Surveillance Ecological Monitoring Protocols")

serialize_shapes = False
serialize_invalid = False
serialize_valid = True


class SPARQLQueryError(Exception):
    pass


def get_xsd_datatype(value_type):
    if value_type == "tern:Text":
        return "string"
    elif value_type == "tern:Boolean":
        return "boolean"
    elif value_type == "tern:Date":
        return "date"
    elif value_type == "tern:DateTime":
        return "dateTime"
    elif value_type == "tern:Float":
        return "float"
    elif value_type == "tern:Integer":
        return "integer"


def sparql_query(url: str, query: str):
    headers = {
        "Content-type": "application/sparql-query",
        "Accept": "application/sparql-results+json",
    }
    r = requests.post(url, headers=headers, data=query)
    try:
        r.raise_for_status()
    except HTTPError as err:
        raise SPARQLQueryError(
            f"Failed fetching data from {url} SPARQL endpoint. Code: {r.status_code} Message: {r.text}."
        ) from err
    return r.json()


q_get_properties_collection_label = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
select ?label where { 
    values ?s {$properties_collection_uri}
	?s skos:prefLabel ?label .
}
"""

q_get_properties_collection_label = string.Template(
    q_get_properties_collection_label
).substitute(properties_collection_uri=f"<{properties_collection_uri}>")

q_get_properties_collection_members = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
select ?properties where { 
    values ?s {$properties_collection_uri}
	?s skos:member ?properties .
}
"""

q_get_properties_collection_members = string.Template(
    q_get_properties_collection_members
).substitute(properties_collection_uri=f"<{properties_collection_uri}>")

properties_collection_file_path = (
    "-".join(
        sparql_query(dawe_endpoint, q_get_properties_collection_label)["results"][
            "bindings"
        ][0]["label"]["value"]
        .lower()
        .replace("module", "")
        .replace("protocol", "")
        .replace("properties", "")
        .replace("observable", "")
        .replace("(", "")
        .replace(")", "")
        .split()
    )
    .replace("--", "-")
    .replace("--", "-")
)

properties_collection_members = [
    i["properties"]["value"]
    for i in sparql_query(dawe_endpoint, q_get_properties_collection_members)[
        "results"
    ]["bindings"]
]

module_folder_file_path = Path("shapes/" + properties_collection_file_path)

module_folder_file_path.mkdir(exist_ok=True)

for property_uri in properties_collection_members:

    # TODO: method_uri should be replaced
    q_get_property_info = """
    select ?featureType ?valueType {
        values ?property_uri {$property_uri}
        ?s <urn:property:featureType> ?featureType ;
        <urn:property:valueType> ?valueType ;
        <urn:property:observableProperty> ?property_uri ;
        <urn:property:protocolModule> <https://linked.data.gov.au/def/test/dawe-cv/576f634e-2706-4f18-b561-0636d4c007d0> .
        }
    """

    q_get_property_info = string.Template(q_get_property_info).substitute(
        property_uri=f"<{property_uri}>"
    )

    property_info_list = sparql_query(dawe_endpoint, q_get_property_info)["results"][
        "bindings"
    ]

    property_feature_type = property_info_list[0]["featureType"]["value"]
    property_value_type = property_info_list[0]["valueType"]["value"]

    q_get_property_label = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    select ?label {
    values ?property_uri {$property_uri}
    ?property_uri skos:prefLabel ?label .
    }
    """

    q_get_property_label = string.Template(q_get_property_label).substitute(
        property_uri=f"<{property_uri}>"
    )

    property_label = sparql_query(dawe_endpoint, q_get_property_label)["results"][
        "bindings"
    ][0]["label"]["value"]

    property_label_file_path = (
        "-".join(property_label.split()).replace("--", "-").replace("--", "-")
    )

    q_get_feature_type_label = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    select ?label {
        values ?s {$feature_type_uri}
        ?s skos:notation ?label .
    }
    """
    q_get_feature_type_label = string.Template(q_get_feature_type_label).substitute(
        feature_type_uri=f"<{property_feature_type}>"
    )

    feature_type_label = sparql_query(tern_endpoint, q_get_feature_type_label)[
        "results"
    ]["bindings"][0]["label"]["value"].replace("-", " ")

    # print(feature_type_label)

    shapes_feature_type_uri = URIRef(
        "urn:shapes:"
        + properties_collection_file_path
        + ":"
        + property_label_file_path
        + ":feature-type"
    )

    feature_type_sh_description = Literal(
        "TERN's ecologists have determined the feature type is _"
        + feature_type_label
        + "_, defined by the link:https://www.publish.csiro.au/book/5230/[Australian Soil and Land Survey Field Handbook]."
    )

    # print(feature_type_sh_description)

    feature_type_sh_message = Literal(
        "The value of `tern:featureType` _MUST_ be link: "
        + property_feature_type
        + "[`"
        + feature_type_label
        + "`]."
    )

    # print(feature_type_sh_message)

    q_shapes_get_feature_type = """
    PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    select ?this  {
        values ?property_uri {$property_uri}
        ?observation a tern:Observation ;
            sosa:observedProperty ?property_uri ;
            sosa:hasFeatureOfInterest ?this .
    }
    """

    q_shapes_get_feature_type = string.Template(q_shapes_get_feature_type).substitute(
        property_uri=f"<{property_uri}>"
    )

    invalid_examples_link = Literal(
        "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes/"
        + properties_collection_file_path
        + "/"
        + property_label_file_path
        + "/invalid.ttl",
        datatype=XSD.anyURI,
    )

    valid_examples_link = Literal(
        "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes/"
        + properties_collection_file_path
        + "/"
        + property_label_file_path
        + "/valid.ttl",
        datatype=XSD.anyURI,
    )

    shapes_link = Literal(
        "https://github.com/ternaustralia/dawe-rlp-spec/blob/main/shapes/"
        + properties_collection_file_path
        + "/"
        + property_label_file_path
        + "/shapes.ttl",
        datatype=XSD.anyURI,
    )

    shapes_simple_result_uri = URIRef(
        "urn:shapes:"
        + properties_collection_file_path
        + ":"
        + property_label_file_path
        + ":simple-result"
    )

    q_shapes_get_simple_result_string1 = """
    PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select $this {
        $this a tern:Observation ;
            sosa:observedProperty 
    """
    q_shapes_get_simple_result_string2 = f"<{property_uri}>"
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

    # print(q_shapes_get_simple_result)

    q_shapes_get_general = """
    PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
    PREFIX unit: <http://qudt.org/vocab/unit/>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?this {
        values ?property_uri {$property_uri}
        ?this a tern:Observation ;
            sosa:observedProperty ?property_uri .
    }
    """

    q_shapes_get_general = string.Template(q_shapes_get_general).substitute(
        property_uri=f"<{property_uri}>"
    )

    shapes_site_visit_uri = URIRef(
        "urn:shapes:"
        + properties_collection_file_path
        + ":"
        + property_label_file_path
        + ":site-visit"
    )

    shapes_used_procedure_uri = URIRef(
        "urn:shapes:"
        + properties_collection_file_path
        + ":"
        + property_label_file_path
        + ":used-procedure"
    )

    shapes_value_type_uri = URIRef(
        "urn:shapes:"
        + properties_collection_file_path
        + ":"
        + property_label_file_path
        + ":value-type"
    )

    q_get_protocol_label = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    select ?label {
        values ?method_uri {$method_uri}
        ?method_uri skos:prefLabel ?label .
    }
    """

    q_get_protocol_label = string.Template(q_get_protocol_label).substitute(
        method_uri=f"<{protocol_module_uri}>"
    )

    protocol_module_label = sparql_query(dawe_endpoint, q_get_protocol_label)[
        "results"
    ]["bindings"][0]["label"]["value"]

    # print(protocol_module_label)

    used_procedure_sh_description = """IRI of procedure _MUST_ have the value `$protocol_module_uri`.

    `$protocol_module_uri` is the IRI for "$protocol_module_label"."""

    used_procedure_sh_description = string.Template(
        used_procedure_sh_description
    ).substitute(
        protocol_module_uri=f"<{protocol_module_uri}>",
        protocol_module_label=f"{protocol_module_label}",
    )

    # print(used_procedure_sh_description)

    used_procedure_sh_message = Literal(
        "The observation's `sosa:usedProcedure` _MUST_ have the value `"
        + protocol_module_uri
        + "`."
    )

    value_type_label = "tern:" + property_value_type.split("/")[-1]

    value_type_sh_description = Literal(
        "The value of `sosa:hasResult` _MUST_ be a `" + value_type_label + "`."
    )

    # print(value_type_sh_description)

    value_type_sh_message = Literal(
        "The result _MUST_ be an instance of `" + value_type_label + "`."
    )

    # print(value_type_sh_message)

    shapes_graph = Graph()
    shapes_graph.bind("sh", SH)
    shapes_graph.bind("dcterms", DCTERMS)
    shapes_graph.bind("reg", REG)

    invalid_graph = Graph()
    invalid_graph.bind("sosa", SOSA)
    invalid_graph.bind("void", VOID)

    valid_graph = Graph()
    valid_graph.bind("sosa", SOSA)
    valid_graph.bind("void", VOID)

    # Add feature type validatio in shapes.ttl
    shapes_graph.add((shapes_feature_type_uri, RDF.type, SH.PropertyShape))
    shapes_graph.add((shapes_feature_type_uri, RDF.type, URNC.Requirement))
    shapes_graph.add((shapes_feature_type_uri, DCTERMS.source, source))
    shapes_graph.add((shapes_feature_type_uri, REG.status, REG.statusSubmitted))
    shapes_graph.add(
        (shapes_feature_type_uri, SH.description, feature_type_sh_description)
    )
    shapes_graph.add(
        (shapes_feature_type_uri, SH.hasValue, URIRef(property_feature_type))
    )
    shapes_graph.add((shapes_feature_type_uri, SH.message, feature_type_sh_message))
    shapes_graph.add((shapes_feature_type_uri, SH.name, Literal("Feature type")))
    shapes_graph.add((shapes_feature_type_uri, SH.path, TERN.featureType))

    feature_type_target_bnode = BNode()
    shapes_graph.add((shapes_feature_type_uri, SH.target, feature_type_target_bnode))
    shapes_graph.add((feature_type_target_bnode, RDF.type, SH.SPARQLTarget))
    shapes_graph.add(
        (feature_type_target_bnode, SH.select, Literal(q_shapes_get_feature_type))
    )

    example_files_bnode = BNode()
    shapes_graph.add((shapes_feature_type_uri, URNP.examples, example_files_bnode))
    shapes_graph.add((example_files_bnode, URNP.invalidExample, invalid_examples_link))
    shapes_graph.add((example_files_bnode, URNP.validExample, valid_examples_link))

    shapes_graph.add((shapes_feature_type_uri, URNP.validator, shapes_link))

    # Add simple result validation in shapes.ttl
    shapes_graph.add((shapes_simple_result_uri, RDF.type, SH.NodeShape))
    shapes_graph.add((shapes_simple_result_uri, RDF.type, URNC.Requirement))
    shapes_graph.add((shapes_simple_result_uri, DCTERMS.source, source))
    shapes_graph.add((shapes_simple_result_uri, REG.status, REG.statusSubmitted))
    shapes_graph.add(
        (
            shapes_simple_result_uri,
            SH.description,
            Literal(
                "Value of `sosa:hasSimpleResult` _MUST_ be the same as the value in `sosa:hasResult`."
            ),
        )
    )
    shapes_graph.add(
        (
            shapes_simple_result_uri,
            SH.message,
            Literal(
                "The observation's `sosa:hasSimpleResult` _MUST_ have a value that is the same as the value in the value node of `sosa:hasResult`."
            ),
        )
    )
    shapes_graph.add((shapes_simple_result_uri, SH.name, Literal("Simple result")))

    simple_result_sparql_bnode = BNode()
    shapes_graph.add((shapes_simple_result_uri, SH.sparql, simple_result_sparql_bnode))
    shapes_graph.add(
        (simple_result_sparql_bnode, SH.select, Literal(q_shapes_get_simple_result))
    )

    shapes_graph.add((shapes_simple_result_uri, SH.targetClass, TERN.Observation))
    shapes_graph.add((shapes_simple_result_uri, URNP.examples, example_files_bnode))
    shapes_graph.add((shapes_simple_result_uri, URNP.validator, shapes_link))

    # Add site visit validation in shapes_graph
    shapes_graph.add((shapes_site_visit_uri, RDF.type, SH.PropertyShape))
    shapes_graph.add((shapes_site_visit_uri, RDF.type, URNC.Requirement))
    shapes_graph.add((shapes_site_visit_uri, DCTERMS.source, source))
    shapes_graph.add((shapes_site_visit_uri, REG.status, REG.statusSubmitted))
    shapes_graph.add(
        (
            shapes_site_visit_uri,
            SH.description,
            Literal(
                "Observations following the "
                + protocol_module_label
                + " are made in the context of a site visit."
            ),
        )
    )
    shapes_graph.add((shapes_site_visit_uri, SH.maxCount, Literal(1)))
    shapes_graph.add(
        (
            shapes_site_visit_uri,
            SH.message,
            Literal("Observations _MUST_ have a value for `tern:hasSiteVisit`."),
        )
    )
    shapes_graph.add((shapes_site_visit_uri, SH.minCount, Literal(1)))
    shapes_graph.add((shapes_site_visit_uri, SH.name, Literal("Site visit")))
    shapes_graph.add((shapes_site_visit_uri, SH.path, TERN.hasSiteVisit))

    site_visit_target_bnode = BNode()
    shapes_graph.add((shapes_site_visit_uri, SH.target, site_visit_target_bnode))
    shapes_graph.add((site_visit_target_bnode, RDF.type, SH.SPARQLTarget))
    shapes_graph.add(
        (site_visit_target_bnode, SH.select, Literal(q_shapes_get_general))
    )

    shapes_graph.add((shapes_site_visit_uri, URNP.examples, example_files_bnode))
    shapes_graph.add((shapes_site_visit_uri, URNP.validator, shapes_link))

    # Add used procedure validation in shapes_graph
    shapes_graph.add((shapes_used_procedure_uri, RDF.type, SH.PropertyShape))
    shapes_graph.add((shapes_used_procedure_uri, RDF.type, URNC.Requirement))
    shapes_graph.add((shapes_used_procedure_uri, DCTERMS.source, source))
    shapes_graph.add((shapes_used_procedure_uri, REG.status, REG.statusSubmitted))
    shapes_graph.add(
        (
            shapes_used_procedure_uri,
            SH.description,
            Literal(used_procedure_sh_description),
        )
    )
    shapes_graph.add(
        (shapes_used_procedure_uri, SH.hasValue, URIRef(protocol_module_uri))
    )
    shapes_graph.add((shapes_used_procedure_uri, SH.message, used_procedure_sh_message))
    shapes_graph.add((shapes_used_procedure_uri, SH.name, Literal("Used procedure")))
    shapes_graph.add((shapes_used_procedure_uri, SH.path, SOSA.usedProcedure))

    used_procedure_target_bnode = BNode()
    shapes_graph.add(
        (shapes_used_procedure_uri, SH.target, used_procedure_target_bnode)
    )
    shapes_graph.add((used_procedure_target_bnode, RDF.type, SH.SPARQLTarget))
    shapes_graph.add(
        (used_procedure_target_bnode, SH.select, Literal(q_shapes_get_general))
    )

    shapes_graph.add((shapes_used_procedure_uri, URNP.examples, example_files_bnode))
    shapes_graph.add((shapes_used_procedure_uri, URNP.validator, shapes_link))

    # Add value type validation in shapes_graph
    shapes_graph.add((shapes_value_type_uri, RDF.type, SH.PropertyShape))
    shapes_graph.add((shapes_value_type_uri, RDF.type, URNC.Requirement))
    shapes_graph.add((shapes_value_type_uri, DCTERMS.source, source))
    shapes_graph.add((shapes_value_type_uri, REG.status, REG.statusSubmitted))
    shapes_graph.add((shapes_value_type_uri, SH["class"], URIRef(property_value_type)))
    shapes_graph.add((shapes_value_type_uri, SH.description, value_type_sh_description))
    shapes_graph.add((shapes_value_type_uri, SH.message, value_type_sh_message))
    shapes_graph.add((shapes_value_type_uri, SH.name, Literal("Value type")))
    shapes_graph.add((shapes_value_type_uri, SH.path, SOSA.hasResult))

    value_type_target_bnode = BNode()
    shapes_graph.add((shapes_value_type_uri, SH.target, value_type_target_bnode))
    shapes_graph.add((value_type_target_bnode, RDF.type, SH.SPARQLTarget))
    shapes_graph.add(
        (value_type_target_bnode, SH.select, Literal(q_shapes_get_general))
    )

    shapes_graph.add((shapes_value_type_uri, URNP.examples, example_files_bnode))
    shapes_graph.add((shapes_value_type_uri, URNP.validator, shapes_link))

    q_shapes_get_result = (
        """
        PREFIX tern: <https://w3id.org/tern/ontologies/tern/>
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?this  {
            ?observation a tern:Observation ;
                sosa:observedProperty 
        """
        + f"<{property_uri}>"
        + """ ;
                sosa:hasResult ?this .
        }"""
    )

    # Add invalid examples in invalid_graph
    invalid_phenomenon_time = URIRef(
        "https://example.com/observation/"
        + property_label_file_path
        + "/b91c54f2-9354-43ee-8412-09974fd2c23c/phenomenonTime"
    )

    invalid_result_time = Literal(
        "2022-09-27T05:38:47.117000+00:00", datatype=XSD.dateTime
    )

    invalid_in_dataset = URIRef("https://example.com/dataset/1")

    # Add the general content of feature type invalid examples in invalid_graph
    invalid_feature_type_uri = URIRef(
        "urn:test:"
        + properties_collection_file_path
        + ":invalid:"
        + property_label_file_path
        + ":feature-type"
    )

    invalid_graph.add((invalid_feature_type_uri, RDF.type, TERN.Observation))
    invalid_graph.add((invalid_feature_type_uri, VOID.inDataset, invalid_in_dataset))
    invalid_graph.add(
        (
            invalid_feature_type_uri,
            RDFS.comment,
            Literal("Invalid result - incorrect feature type."),
        )
    )

    invalid_feature_type_feature_of_interest_bnode = BNode()
    invalid_graph.add(
        (
            invalid_feature_type_uri,
            SOSA.hasFeatureOfInterest,
            invalid_feature_type_feature_of_interest_bnode,
        )
    )
    invalid_graph.add(
        (
            invalid_feature_type_feature_of_interest_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    invalid_graph.add(
        (
            invalid_feature_type_feature_of_interest_bnode,
            VOID.inDataset,
            invalid_in_dataset,
        )
    )
    invalid_graph.add(
        (
            invalid_feature_type_feature_of_interest_bnode,
            TERN.featureType,
            URIRef("urn:fake:feature-type"),
        )
    )

    invalid_feature_type_result_bnode = BNode()
    invalid_graph.add(
        (invalid_feature_type_uri, SOSA.hasResult, invalid_feature_type_result_bnode)
    )
    invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.Value))
    invalid_graph.add(
        (invalid_feature_type_result_bnode, SOSA.isResultOf, invalid_feature_type_uri)
    )

    invalid_graph.add(
        (invalid_feature_type_uri, SOSA.ObservableProperty, URIRef(property_uri))
    )
    invalid_graph.add(
        (invalid_feature_type_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
    )
    invalid_graph.add((invalid_feature_type_uri, SOSA.resultTime, invalid_result_time))
    invalid_graph.add(
        (invalid_feature_type_uri, SOSA.usedProcedure, URIRef(protocol_module_uri))
    )
    invalid_graph.add(
        (invalid_feature_type_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
    )

    # Add the general content of value type invalid examples in invalid_graph
    invalid_value_type_uri = URIRef(
        "urn:test:"
        + properties_collection_file_path
        + ":invalid:"
        + property_label_file_path
        + ":value-type"
    )

    invalid_graph.add((invalid_value_type_uri, RDF.type, TERN.Observation))
    invalid_graph.add((invalid_value_type_uri, VOID.inDataset, invalid_in_dataset))
    invalid_graph.add(
        (
            invalid_value_type_uri,
            RDFS.comment,
            Literal(
                "Invalid result - the value of the result node must be `"
                + str(value_type_label)
                + "`."
            ),
        )
    )

    invalid_value_type_feature_of_interest_bnode = BNode()
    invalid_graph.add(
        (
            invalid_value_type_uri,
            SOSA.hasFeatureOfInterest,
            invalid_value_type_feature_of_interest_bnode,
        )
    )
    invalid_graph.add(
        (
            invalid_value_type_feature_of_interest_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    invalid_graph.add(
        (
            invalid_value_type_feature_of_interest_bnode,
            VOID.inDataset,
            invalid_in_dataset,
        )
    )
    invalid_graph.add(
        (
            invalid_value_type_feature_of_interest_bnode,
            TERN.featureType,
            URIRef(property_feature_type),
        )
    )

    invalid_value_type_result_bnode = BNode()
    invalid_graph.add(
        (invalid_value_type_uri, SOSA.hasResult, invalid_value_type_result_bnode)
    )
    invalid_graph.add((invalid_value_type_result_bnode, RDF.type, TERN.Value))
    invalid_graph.add(
        (invalid_value_type_result_bnode, SOSA.isResultOf, invalid_value_type_uri)
    )

    invalid_graph.add(
        (invalid_value_type_uri, SOSA.ObservableProperty, URIRef(property_uri))
    )
    invalid_graph.add(
        (invalid_value_type_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
    )
    invalid_graph.add((invalid_value_type_uri, SOSA.resultTime, invalid_result_time))
    invalid_graph.add(
        (invalid_value_type_uri, SOSA.usedProcedure, URIRef(protocol_module_uri))
    )
    invalid_graph.add(
        (invalid_value_type_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
    )

    # Add the general content of site visit invalid examples in invalid_graph
    invalid_site_visit_uri = URIRef(
        "urn:test:"
        + properties_collection_file_path
        + ":invalid:"
        + property_label_file_path
        + ":site-visit"
    )

    invalid_graph.add((invalid_site_visit_uri, RDF.type, TERN.Observation))
    invalid_graph.add((invalid_site_visit_uri, VOID.inDataset, invalid_in_dataset))
    invalid_graph.add(
        (
            invalid_site_visit_uri,
            RDFS.comment,
            Literal("Invalid result - all observations must have a site vist."),
        )
    )

    invalid_site_visit_feature_of_interest_bnode = BNode()
    invalid_graph.add(
        (
            invalid_site_visit_uri,
            SOSA.hasFeatureOfInterest,
            invalid_site_visit_feature_of_interest_bnode,
        )
    )
    invalid_graph.add(
        (
            invalid_site_visit_feature_of_interest_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    invalid_graph.add(
        (
            invalid_site_visit_feature_of_interest_bnode,
            VOID.inDataset,
            invalid_in_dataset,
        )
    )
    invalid_graph.add(
        (
            invalid_site_visit_feature_of_interest_bnode,
            TERN.featureType,
            URIRef(property_feature_type),
        )
    )

    invalid_site_visit_result_bnode = BNode()
    invalid_graph.add(
        (invalid_site_visit_uri, SOSA.hasResult, invalid_site_visit_result_bnode)
    )
    invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.Value))
    invalid_graph.add(
        (invalid_site_visit_result_bnode, SOSA.isResultOf, invalid_site_visit_uri)
    )

    invalid_graph.add(
        (invalid_site_visit_uri, SOSA.ObservableProperty, URIRef(property_uri))
    )
    invalid_graph.add(
        (invalid_site_visit_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
    )
    invalid_graph.add((invalid_site_visit_uri, SOSA.resultTime, invalid_result_time))
    invalid_graph.add(
        (invalid_site_visit_uri, SOSA.usedProcedure, URIRef(protocol_module_uri))
    )

    # Add the general content of simple result invalid examples in invalid_graph
    invalid_simple_result_uri = URIRef(
        "urn:test:"
        + properties_collection_file_path
        + ":invalid:"
        + property_label_file_path
        + ":simple-result"
    )

    invalid_graph.add((invalid_simple_result_uri, RDF.type, TERN.Observation))
    invalid_graph.add((invalid_simple_result_uri, VOID.inDataset, invalid_in_dataset))
    invalid_graph.add(
        (
            invalid_simple_result_uri,
            RDFS.comment,
            Literal(
                "Invalid result - The value in simple result must be same with that in the result node."
            ),
        )
    )

    invalid_simple_result_feature_of_interest_bnode = BNode()
    invalid_graph.add(
        (
            invalid_simple_result_uri,
            SOSA.hasFeatureOfInterest,
            invalid_simple_result_feature_of_interest_bnode,
        )
    )
    invalid_graph.add(
        (
            invalid_simple_result_feature_of_interest_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    invalid_graph.add(
        (
            invalid_simple_result_feature_of_interest_bnode,
            VOID.inDataset,
            invalid_in_dataset,
        )
    )
    invalid_graph.add(
        (
            invalid_simple_result_feature_of_interest_bnode,
            TERN.featureType,
            URIRef(property_feature_type),
        )
    )

    invalid_simple_result_result_bnode = BNode()
    invalid_graph.add(
        (invalid_simple_result_uri, SOSA.hasResult, invalid_simple_result_result_bnode)
    )
    invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.Value))
    invalid_graph.add(
        (invalid_simple_result_result_bnode, SOSA.isResultOf, invalid_simple_result_uri)
    )

    invalid_graph.add(
        (invalid_simple_result_uri, SOSA.ObservableProperty, URIRef(property_uri))
    )
    invalid_graph.add(
        (invalid_simple_result_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
    )
    invalid_graph.add((invalid_simple_result_uri, SOSA.resultTime, invalid_result_time))
    invalid_graph.add(
        (invalid_simple_result_uri, SOSA.usedProcedure, URIRef(protocol_module_uri))
    )
    invalid_graph.add(
        (invalid_simple_result_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
    )

    # Add the general content of used procedure invalid examples in invalid_graph
    invalid_used_procedure_uri = URIRef(
        "urn:test:"
        + properties_collection_file_path
        + ":invalid:"
        + property_label_file_path
        + ":used-procedure"
    )

    invalid_graph.add((invalid_used_procedure_uri, RDF.type, TERN.Observation))
    invalid_graph.add((invalid_used_procedure_uri, VOID.inDataset, invalid_in_dataset))
    invalid_graph.add(
        (
            invalid_used_procedure_uri,
            RDFS.comment,
            Literal(
                "Invalid result - the used procedure should be '"
                + str(protocol_module_label)
                + "'."
            ),
        )
    )

    invalid_used_procedure_feature_of_interest_bnode = BNode()
    invalid_graph.add(
        (
            invalid_used_procedure_uri,
            SOSA.hasFeatureOfInterest,
            invalid_used_procedure_feature_of_interest_bnode,
        )
    )
    invalid_graph.add(
        (
            invalid_used_procedure_feature_of_interest_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    invalid_graph.add(
        (
            invalid_used_procedure_feature_of_interest_bnode,
            VOID.inDataset,
            invalid_in_dataset,
        )
    )
    invalid_graph.add(
        (
            invalid_used_procedure_feature_of_interest_bnode,
            TERN.featureType,
            URIRef(property_feature_type),
        )
    )

    invalid_used_procedure_result_bnode = BNode()
    invalid_graph.add(
        (
            invalid_used_procedure_uri,
            SOSA.hasResult,
            invalid_used_procedure_result_bnode,
        )
    )
    invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.Value))
    invalid_graph.add(
        (
            invalid_used_procedure_result_bnode,
            SOSA.isResultOf,
            invalid_used_procedure_uri,
        )
    )

    invalid_graph.add(
        (invalid_used_procedure_uri, SOSA.ObservableProperty, URIRef(property_uri))
    )
    invalid_graph.add(
        (invalid_used_procedure_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
    )
    invalid_graph.add(
        (invalid_used_procedure_uri, SOSA.resultTime, invalid_result_time)
    )
    invalid_graph.add(
        (invalid_used_procedure_uri, SOSA.usedProcedure, URIRef("urn:fake:procedure"))
    )
    invalid_graph.add(
        (invalid_used_procedure_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
    )

    # Add the general content for valid examples

    valid_example_uri = URIRef(
        "urn:test:"
        + properties_collection_file_path
        + ":valid:"
        + property_label_file_path
    )

    valid_graph.add((valid_example_uri, RDF.type, TERN.Observation))
    valid_graph.add((valid_example_uri, VOID.inDataset, invalid_in_dataset))
    valid_graph.add(
        (
            valid_example_uri,
            RDFS.comment,
            Literal("Valid result for observable property - " + str(property_label)),
        )
    )

    valid_feature_of_interest_bnode = BNode()
    valid_graph.add(
        (
            valid_example_uri,
            SOSA.hasFeatureOfInterest,
            valid_feature_of_interest_bnode,
        )
    )
    valid_graph.add(
        (
            valid_feature_of_interest_bnode,
            RDF.type,
            TERN.FeatureOfInterest,
        )
    )
    valid_graph.add(
        (
            valid_feature_of_interest_bnode,
            VOID.inDataset,
            invalid_in_dataset,
        )
    )
    valid_graph.add(
        (
            valid_feature_of_interest_bnode,
            TERN.featureType,
            URIRef(property_feature_type),
        )
    )

    valid_result_bnode = BNode()
    valid_graph.add(
        (
            valid_example_uri,
            SOSA.hasResult,
            valid_result_bnode,
        )
    )
    valid_graph.add((valid_result_bnode, RDF.type, TERN.Value))
    valid_graph.add(
        (
            valid_result_bnode,
            SOSA.isResultOf,
            valid_example_uri,
        )
    )

    valid_graph.add((valid_example_uri, SOSA.ObservableProperty, URIRef(property_uri)))
    valid_graph.add((valid_example_uri, SOSA.phenomenonTime, invalid_phenomenon_time))
    valid_graph.add((valid_example_uri, SOSA.resultTime, invalid_result_time))
    valid_graph.add(
        (valid_example_uri, SOSA.usedProcedure, URIRef(protocol_module_uri))
    )
    valid_graph.add((valid_example_uri, TERN.hasSiteVisit, URIRef("urn:test:site")))

    # Add the general content of datatype invalid examples in invalid_graph
    if URIRef(property_value_type) != TERN.IRI:
        invalid_datatype_uri = URIRef(
            "urn:test:"
            + properties_collection_file_path
            + ":invalid:"
            + property_label_file_path
            + ":datatype"
        )

        invalid_graph.add((invalid_datatype_uri, RDF.type, TERN.Observation))
        invalid_graph.add((invalid_datatype_uri, VOID.inDataset, invalid_in_dataset))
        invalid_graph.add(
            (
                invalid_datatype_uri,
                RDFS.comment,
                Literal(
                    "Invalid result - the datatype of the value of the result node must be `xsd:"
                    + get_xsd_datatype(value_type_label)
                    + "`."
                ),
            )
        )

        invalid_datatype_feature_of_interest_bnode = BNode()
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasFeatureOfInterest,
                invalid_datatype_feature_of_interest_bnode,
            )
        )
        invalid_graph.add(
            (
                invalid_datatype_feature_of_interest_bnode,
                RDF.type,
                TERN.FeatureOfInterest,
            )
        )
        invalid_graph.add(
            (
                invalid_datatype_feature_of_interest_bnode,
                VOID.inDataset,
                invalid_in_dataset,
            )
        )
        invalid_graph.add(
            (
                invalid_datatype_feature_of_interest_bnode,
                TERN.featureType,
                URIRef(property_feature_type),
            )
        )

        invalid_datatype_result_bnode = BNode()
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasResult,
                invalid_datatype_result_bnode,
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.Value))
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                SOSA.isResultOf,
                invalid_datatype_uri,
            )
        )

        invalid_graph.add(
            (invalid_datatype_uri, SOSA.ObservableProperty, URIRef(property_uri))
        )
        invalid_graph.add(
            (invalid_datatype_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
        )
        invalid_graph.add((invalid_datatype_uri, SOSA.resultTime, invalid_result_time))
        invalid_graph.add(
            (invalid_datatype_uri, SOSA.usedProcedure, URIRef(protocol_module_uri))
        )
        invalid_graph.add(
            (invalid_datatype_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
        )

    if URIRef(property_value_type) in [TERN.Integer, TERN.Float]:
        # Add the general content of value range validation in shapes_graph
        shapes_value_range_uri = URIRef(
            "urn:shapes:"
            + properties_collection_file_path
            + ":"
            + property_label_file_path
            + ":value-range"
        )

        value_range_sh_description = (
            "Value _MUST_ be between "
            + values_tbd
            + " and "
            + values_tbd
            + " inclusive."
        )

        value_range_sh_message = (
            "The result _MUST_ have a value between "
            + values_tbd
            + " and "
            + values_tbd
            + " inclusively."
        )

        shapes_graph.add((shapes_value_range_uri, RDF.type, SH.PropertyShape))
        shapes_graph.add((shapes_value_range_uri, RDF.type, URNC.Requirement))
        shapes_graph.add((shapes_value_range_uri, DCTERMS.source, source))
        shapes_graph.add((shapes_value_range_uri, REG.status, REG.statusSubmitted))
        shapes_graph.add(
            (
                shapes_value_range_uri,
                SH.description,
                Literal(value_range_sh_description),
            )
        )
        shapes_graph.add((shapes_value_range_uri, SH.maxInclusive, URIRef(values_tbd)))
        shapes_graph.add(
            (shapes_value_range_uri, SH.message, Literal(value_range_sh_message))
        )
        shapes_graph.add((shapes_value_range_uri, SH.minInclusive, URIRef(values_tbd)))
        shapes_graph.add((shapes_value_range_uri, SH.name, Literal("Value range")))
        shapes_graph.add((shapes_value_range_uri, SH.path, RDF.value))

        value_range_target_bnode = BNode()
        shapes_graph.add((shapes_value_range_uri, SH.target, value_range_target_bnode))
        shapes_graph.add((value_range_target_bnode, RDF.type, SH.SPARQLTarget))
        shapes_graph.add(
            (value_range_target_bnode, SH.select, Literal(q_shapes_get_result))
        )

        shapes_graph.add((shapes_value_range_uri, URNP.examples, example_files_bnode))
        shapes_graph.add((shapes_value_range_uri, URNP.validator, shapes_link))

        # Add value range invalid examples in invalid_graph
        invalid_value_range_uri = URIRef(
            "urn:test:"
            + properties_collection_file_path
            + ":invalid:"
            + property_label_file_path
            + ":value-range"
        )

        invalid_graph.add((invalid_value_range_uri, RDF.type, TERN.Observation))
        invalid_graph.add((invalid_value_range_uri, VOID.inDataset, invalid_in_dataset))
        invalid_graph.add(
            (
                invalid_value_range_uri,
                RDFS.comment,
                Literal("Invalid result - value out of range"),
            )
        )

        invalid_value_range_feature_of_interest_bnode = BNode()
        invalid_graph.add(
            (
                invalid_value_range_uri,
                SOSA.hasFeatureOfInterest,
                invalid_value_range_feature_of_interest_bnode,
            )
        )
        invalid_graph.add(
            (
                invalid_value_range_feature_of_interest_bnode,
                RDF.type,
                TERN.FeatureOfInterest,
            )
        )
        invalid_graph.add(
            (
                invalid_value_range_feature_of_interest_bnode,
                VOID.inDataset,
                invalid_in_dataset,
            )
        )
        invalid_graph.add(
            (
                invalid_value_range_feature_of_interest_bnode,
                TERN.featureType,
                URIRef(property_feature_type),
            )
        )

        invalid_value_range_result_bnode = BNode()
        invalid_graph.add(
            (
                invalid_value_range_uri,
                SOSA.hasResult,
                invalid_value_range_result_bnode,
            )
        )
        invalid_graph.add((invalid_value_range_result_bnode, RDF.type, TERN.Value))
        invalid_graph.add(
            (
                invalid_value_range_result_bnode,
                SOSA.isResultOf,
                invalid_value_range_uri,
            )
        )

        invalid_graph.add(
            (
                invalid_value_range_result_bnode,
                TERN.unit,
                URIRef(values_tbd),
            )
        )

        invalid_graph.add(
            (invalid_value_range_uri, SOSA.ObservableProperty, URIRef(property_uri))
        )
        invalid_graph.add(
            (invalid_value_range_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
        )
        invalid_graph.add(
            (invalid_value_range_uri, SOSA.resultTime, invalid_result_time)
        )
        invalid_graph.add(
            (
                invalid_value_range_uri,
                SOSA.usedProcedure,
                URIRef(protocol_module_uri),
            )
        )
        invalid_graph.add(
            (invalid_value_range_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
        )

    elif URIRef(property_value_type) in [
        TERN.Text,
        TERN.Boolean,
        TERN.Date,
        TERN.DateTime,
    ]:
        # Add the general content of datatype validation in shapes_graph
        shapes_datatype_uri = URIRef(
            "urn:shapes:"
            + properties_collection_file_path
            + ":"
            + property_label_file_path
            + ":datatype"
        )

        datatype_sh_description = (
            "The value in `sosa:hasResult` _MUST_ be xsd:"
            + get_xsd_datatype(value_type_label)
            + "."
        )

        datatype_sh_message = (
            "The value of `rdf:value` _MUST_ have the datatype xsd:"
            + get_xsd_datatype(value_type_label)
            + "."
        )

        shapes_graph.add((shapes_datatype_uri, RDF.type, SH.PropertyShape))
        shapes_graph.add((shapes_datatype_uri, RDF.type, URNC.Requirement))
        shapes_graph.add((shapes_datatype_uri, DCTERMS.source, source))
        shapes_graph.add((shapes_datatype_uri, REG.status, REG.statusSubmitted))
        shapes_graph.add(
            (shapes_datatype_uri, SH.description, Literal(datatype_sh_description))
        )
        shapes_graph.add(
            (shapes_datatype_uri, SH.message, Literal(datatype_sh_message))
        )
        shapes_graph.add((shapes_datatype_uri, SH.name, Literal("Datatype")))
        shapes_graph.add((shapes_datatype_uri, SH.path, RDF.value))

        datatype_target_bnode = BNode()
        shapes_graph.add((shapes_datatype_uri, SH.target, datatype_target_bnode))
        shapes_graph.add((datatype_target_bnode, RDF.type, SH.SPARQLTarget))
        shapes_graph.add(
            (datatype_target_bnode, SH.select, Literal(q_shapes_get_result))
        )

        shapes_graph.add((shapes_datatype_uri, URNP.examples, example_files_bnode))
        shapes_graph.add((shapes_datatype_uri, URNP.validator, shapes_link))

    # Add specific patterns for each value type
    # for categorical properties
    if URIRef(property_value_type) == TERN.IRI:

        q_get_categorical_collection_uri_label = """
        PREFIX urnp: <urn:property:>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        select ?categoricalCollectionURI ?categoricalCollectionLabel {
            values ?property_uri {$property_uri}
            ?s urnp:categoricalValuesCollection ?categoricalCollectionURI ;
            urnp:observableProperty ?property_uri ;
            urnp:protocolModule <https://linked.data.gov.au/def/test/dawe-cv/576f634e-2706-4f18-b561-0636d4c007d0> .
            ?categoricalCollectionURI skos:prefLabel ?categoricalCollectionLabel .
        }
        """

        q_get_categorical_collection_uri_label = string.Template(
            q_get_categorical_collection_uri_label
        ).substitute(property_uri=f"<{property_uri}>")

        property_categorical_collection_uri_label_json = sparql_query(
            dawe_endpoint, q_get_categorical_collection_uri_label
        )

        property_categorical_collection_uri = (
            property_categorical_collection_uri_label_json["results"]["bindings"][0][
                "categoricalCollectionURI"
            ]["value"]
        )

        property_categorical_collection_label = (
            property_categorical_collection_uri_label_json["results"]["bindings"][0][
                "categoricalCollectionLabel"
            ]["value"]
        )

        result_value_sh_description = Literal(
            "The value in `sosa:hasResult` _MUST_ be a value in `sh:in`, which is the "
            + property_categorical_collection_label
            + " controlled vocabulary."
        )

        result_value_sh_message = Literal(
            "The value of `rdf:value` _MUST_ exist in the "
            + property_categorical_collection_label
            + " controlled vocabulary."
        )

        categorical_collection_uuid = property_categorical_collection_uri.split("/")[-1]

        q_shapes_get_categorical_values = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        select ?values {
            values ?categoricalUUID {$categorical_collection_uuid}
            ?s skos:member ?values .
            filter (STRENDS(str(?s), ?categoricalUUID))
        }
        """

        q_shapes_get_categorical_values = string.Template(
            q_shapes_get_categorical_values
        ).substitute(categorical_collection_uuid=f"'{categorical_collection_uuid}'")

        shapes_result_value_uri = URIRef(
            "urn:shapes:"
            + properties_collection_file_path
            + ":"
            + property_label_file_path
            + ":result-value"
        )

        # Add result value validation in shapes_graph
        shapes_graph.add((shapes_result_value_uri, RDF.type, SH.PropertyShape))
        shapes_graph.add((shapes_result_value_uri, RDF.type, URNC.Controlled))
        shapes_graph.add((shapes_result_value_uri, RDF.type, URNC.Requirement))
        shapes_graph.add((shapes_result_value_uri, DCTERMS.source, source))
        shapes_graph.add((shapes_result_value_uri, REG.status, REG.statusSubmitted))
        shapes_graph.add(
            (shapes_result_value_uri, SH.description, result_value_sh_description)
        )
        shapes_graph.add((shapes_result_value_uri, SH["in"], BNode()))
        shapes_graph.add((shapes_result_value_uri, SH.message, result_value_sh_message))
        shapes_graph.add((shapes_result_value_uri, SH.name, Literal("Result value")))
        shapes_graph.add((shapes_result_value_uri, SH.path, RDF.value))

        result_value_target_bnode = BNode()
        shapes_graph.add(
            (shapes_result_value_uri, SH.target, result_value_target_bnode)
        )
        shapes_graph.add((result_value_target_bnode, RDF.type, SH.SPARQLTarget))
        shapes_graph.add(
            (result_value_target_bnode, SH.select, Literal(q_shapes_get_result))
        )

        shapes_graph.add((shapes_result_value_uri, URNP.examples, example_files_bnode))
        shapes_graph.add(
            (
                shapes_result_value_uri,
                URNP.query,
                Literal(q_shapes_get_categorical_values),
            )
        )
        shapes_graph.add(
            (shapes_result_value_uri, URNP.sparqlEndpoint, Literal(dawe_endpoint))
        )
        shapes_graph.add((shapes_result_value_uri, URNP.validator, shapes_link))

        # Add vocabulary validation in shapes_graph
        shapes_vocabulary_uri = URIRef(
            "urn:shapes:"
            + properties_collection_file_path
            + ":"
            + property_label_file_path
            + ":vocabulary"
        )

        vocabulary_sh_description = """IRI of `tern:vocabulary` in `sosa:hasResult` _MUST_ have the value `$property_categorical_collection_uri`.

        `$property_categorical_collection_uri` is the IRI for "$property_categorical_collection_label"."""

        vocabulary_sh_description = string.Template(
            vocabulary_sh_description
        ).substitute(
            property_categorical_collection_uri=f"<{property_categorical_collection_uri}>",
            property_categorical_collection_label=f"{property_categorical_collection_label}",
        )

        vocabulary_sh_message = (
            "The value of `tern:vocabulary` _MUST_ match the pattern `"
            + str(categorical_collection_uuid)
            + "$`."
        )

        shapes_graph.add((shapes_vocabulary_uri, RDF.type, SH.PropertyShape))
        shapes_graph.add((shapes_vocabulary_uri, RDF.type, URNC.Requirement))
        shapes_graph.add((shapes_vocabulary_uri, DCTERMS.source, source))
        shapes_graph.add((shapes_vocabulary_uri, REG.status, REG.statusSubmitted))
        shapes_graph.add(
            (shapes_vocabulary_uri, SH.description, Literal(vocabulary_sh_description))
        )
        shapes_graph.add(
            (shapes_vocabulary_uri, SH.message, Literal(vocabulary_sh_message))
        )
        shapes_graph.add((shapes_vocabulary_uri, SH.name, Literal("Vocabulary")))
        shapes_graph.add((shapes_vocabulary_uri, SH.path, TERN.vocabulary))
        shapes_graph.add(
            (
                shapes_vocabulary_uri,
                SH.pattern,
                Literal(str(categorical_collection_uuid) + "$"),
            )
        )

        vocabulary_target_bnode = BNode()
        shapes_graph.add((shapes_vocabulary_uri, SH.target, vocabulary_target_bnode))
        shapes_graph.add((vocabulary_target_bnode, RDF.type, SH.SPARQLTarget))
        shapes_graph.add(
            (vocabulary_target_bnode, SH.select, Literal(q_shapes_get_result))
        )

        shapes_graph.add((shapes_vocabulary_uri, URNP.examples, example_files_bnode))
        shapes_graph.add((shapes_vocabulary_uri, URNP.validator, shapes_link))

        # Add invalid examples in invalid_graph

        q_get_vocabulary_instance = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        select ?instance {
            values ?s {$vocabulary_uri}
            ?s skos:member ?instance .
        } limit 1
        """
        q_get_vocabulary_instance = string.Template(
            q_get_vocabulary_instance
        ).substitute(vocabulary_uri=f"<{property_categorical_collection_uri}>")

        vocabulary_instance = sparql_query(dawe_endpoint, q_get_vocabulary_instance)[
            "results"
        ]["bindings"][0]["instance"]["value"]

        # print(vocabulary_instance)

        # Add result value invalid examples in invalid_graph
        invalid_result_value_uri = URIRef(
            "urn:test:"
            + properties_collection_file_path
            + ":invalid:"
            + property_label_file_path
            + ":result-value"
        )

        invalid_graph.add((invalid_result_value_uri, RDF.type, TERN.Observation))
        invalid_graph.add(
            (invalid_result_value_uri, VOID.inDataset, invalid_in_dataset)
        )
        invalid_graph.add(
            (
                invalid_result_value_uri,
                RDFS.comment,
                Literal(
                    "Invalid result - value not from the controlled vocabulary list"
                ),
            )
        )

        invalid_result_value_feature_of_interest_bnode = BNode()
        invalid_graph.add(
            (
                invalid_result_value_uri,
                SOSA.hasFeatureOfInterest,
                invalid_result_value_feature_of_interest_bnode,
            )
        )
        invalid_graph.add(
            (
                invalid_result_value_feature_of_interest_bnode,
                RDF.type,
                TERN.FeatureOfInterest,
            )
        )
        invalid_graph.add(
            (
                invalid_result_value_feature_of_interest_bnode,
                VOID.inDataset,
                invalid_in_dataset,
            )
        )
        invalid_graph.add(
            (
                invalid_result_value_feature_of_interest_bnode,
                TERN.featureType,
                URIRef(property_feature_type),
            )
        )

        invalid_result_value_result_bnode = BNode()
        invalid_graph.add(
            (
                invalid_result_value_uri,
                SOSA.hasResult,
                invalid_result_value_result_bnode,
            )
        )
        invalid_graph.add((invalid_result_value_result_bnode, RDF.type, TERN.Value))
        invalid_graph.add((invalid_result_value_result_bnode, RDF.type, TERN.IRI))
        invalid_graph.add(
            (
                invalid_result_value_result_bnode,
                RDF.value,
                URIRef("urn:fake:categorical:value"),
            )
        )
        invalid_graph.add(
            (
                invalid_result_value_result_bnode,
                SOSA.isResultOf,
                invalid_result_value_uri,
            )
        )
        invalid_graph.add(
            (
                invalid_result_value_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )

        invalid_graph.add(
            (
                invalid_result_value_uri,
                SOSA.hasSimpleResult,
                URIRef("urn:fake:categorical:value"),
            )
        )

        invalid_graph.add(
            (invalid_result_value_uri, SOSA.ObservableProperty, URIRef(property_uri))
        )
        invalid_graph.add(
            (invalid_result_value_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
        )
        invalid_graph.add(
            (invalid_result_value_uri, SOSA.resultTime, invalid_result_time)
        )
        invalid_graph.add(
            (
                invalid_result_value_uri,
                SOSA.usedProcedure,
                URIRef(protocol_module_uri),
            )
        )
        invalid_graph.add(
            (invalid_result_value_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
        )

        # Add vocabulary invalid examples in invalid_graph
        invalid_vocabulary_uri = URIRef(
            "urn:test:"
            + properties_collection_file_path
            + ":invalid:"
            + property_label_file_path
            + ":vocabulary"
        )

        invalid_graph.add((invalid_vocabulary_uri, RDF.type, TERN.Observation))
        invalid_graph.add((invalid_vocabulary_uri, VOID.inDataset, invalid_in_dataset))
        invalid_graph.add(
            (
                invalid_vocabulary_uri,
                RDFS.comment,
                Literal("Invalid result - incorrect vocabulary"),
            )
        )

        invalid_vocabulary_feature_of_interest_bnode = BNode()
        invalid_graph.add(
            (
                invalid_vocabulary_uri,
                SOSA.hasFeatureOfInterest,
                invalid_vocabulary_feature_of_interest_bnode,
            )
        )
        invalid_graph.add(
            (
                invalid_vocabulary_feature_of_interest_bnode,
                RDF.type,
                TERN.FeatureOfInterest,
            )
        )
        invalid_graph.add(
            (
                invalid_vocabulary_feature_of_interest_bnode,
                VOID.inDataset,
                invalid_in_dataset,
            )
        )
        invalid_graph.add(
            (
                invalid_vocabulary_feature_of_interest_bnode,
                TERN.featureType,
                URIRef(property_feature_type),
            )
        )

        invalid_vocabulary_result_bnode = BNode()
        invalid_graph.add(
            (
                invalid_vocabulary_uri,
                SOSA.hasResult,
                invalid_vocabulary_result_bnode,
            )
        )
        invalid_graph.add((invalid_vocabulary_result_bnode, RDF.type, TERN.Value))
        invalid_graph.add((invalid_vocabulary_result_bnode, RDF.type, TERN.IRI))
        invalid_graph.add(
            (
                invalid_vocabulary_result_bnode,
                RDF.value,
                URIRef(vocabulary_instance),
            )
        )
        invalid_graph.add(
            (
                invalid_vocabulary_result_bnode,
                SOSA.isResultOf,
                invalid_vocabulary_uri,
            )
        )
        invalid_graph.add(
            (
                invalid_vocabulary_result_bnode,
                TERN.vocabulary,
                URIRef("urn:fake:vocabulary"),
            )
        )

        invalid_graph.add(
            (
                invalid_vocabulary_uri,
                SOSA.hasSimpleResult,
                URIRef(vocabulary_instance),
            )
        )

        invalid_graph.add(
            (invalid_vocabulary_uri, SOSA.ObservableProperty, URIRef(property_uri))
        )
        invalid_graph.add(
            (invalid_vocabulary_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
        )
        invalid_graph.add(
            (invalid_vocabulary_uri, SOSA.resultTime, invalid_result_time)
        )
        invalid_graph.add(
            (
                invalid_vocabulary_uri,
                SOSA.usedProcedure,
                URIRef(protocol_module_uri),
            )
        )
        invalid_graph.add(
            (invalid_vocabulary_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
        )

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (invalid_feature_type_result_bnode, RDF.value, URIRef(vocabulary_instance))
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.IRI))
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                URIRef(vocabulary_instance),
            )
        )

        # in value type
        invalid_graph.add(
            (invalid_value_type_result_bnode, RDF.value, URIRef(vocabulary_instance))
        )
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )
        invalid_graph.add(
            (invalid_value_type_uri, SOSA.hasSimpleResult, URIRef(vocabulary_instance))
        )

        # in site visit
        invalid_graph.add(
            (invalid_site_visit_result_bnode, RDF.value, URIRef(vocabulary_instance))
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.IRI))
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )
        invalid_graph.add(
            (invalid_site_visit_uri, SOSA.hasSimpleResult, URIRef(vocabulary_instance))
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                URIRef(vocabulary_instance),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.IRI))
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                URIRef("urn:fake:categorical:value"),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                URIRef(vocabulary_instance),
            )
        )
        invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.IRI))
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                URIRef(vocabulary_instance),
            )
        )

        # Add valid examples
        valid_graph.add(
            (valid_example_uri, SOSA.hasSimpleResult, URIRef(vocabulary_instance))
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.IRI))
        valid_graph.add((valid_result_bnode, RDF.value, URIRef(vocabulary_instance)))
        valid_graph.add(
            (
                valid_result_bnode,
                TERN.vocabulary,
                URIRef(property_categorical_collection_uri),
            )
        )

    elif URIRef(property_value_type) == TERN.Float:
        shapes_graph.add((shapes_value_range_uri, SH.datatype, XSD.float))

        # Add the unit of measure validation in shapes_graph
        shapes_unit_of_measure_uri = URIRef(
            "urn:shapes:"
            + properties_collection_file_path
            + ":"
            + property_label_file_path
            + ":unit-of-measure"
        )

        unit_of_measure_sh_description = (
            "Result value's unit of measure _MUST_ have the value `" + values_tbd + "`."
        )

        unit_of_measure_sh_message = (
            "The result _MUST_ have `" + values_tbd + "` as the value for `tern:unit`."
        )

        shapes_graph.add((shapes_unit_of_measure_uri, RDF.type, SH.PropertyShape))
        shapes_graph.add((shapes_unit_of_measure_uri, RDF.type, URNC.Requirement))
        shapes_graph.add((shapes_unit_of_measure_uri, DCTERMS.source, source))
        shapes_graph.add((shapes_unit_of_measure_uri, REG.status, REG.statusSubmitted))
        shapes_graph.add(
            (
                shapes_unit_of_measure_uri,
                SH.description,
                Literal(unit_of_measure_sh_description),
            )
        )
        shapes_graph.add((shapes_unit_of_measure_uri, SH.hasValue, URIRef(values_tbd)))
        shapes_graph.add(
            (
                shapes_unit_of_measure_uri,
                SH.message,
                Literal(unit_of_measure_sh_message),
            )
        )
        shapes_graph.add(
            (shapes_unit_of_measure_uri, SH.name, Literal("Unit of measure"))
        )
        shapes_graph.add((shapes_unit_of_measure_uri, SH.path, TERN.unit))

        unit_of_measure_target_bnode = BNode()
        shapes_graph.add(
            (shapes_unit_of_measure_uri, SH.target, unit_of_measure_target_bnode)
        )
        shapes_graph.add((unit_of_measure_target_bnode, RDF.type, SH.SPARQLTarget))
        shapes_graph.add(
            (unit_of_measure_target_bnode, SH.select, Literal(q_shapes_get_result))
        )

        shapes_graph.add(
            (shapes_unit_of_measure_uri, URNP.examples, example_files_bnode)
        )
        shapes_graph.add((shapes_unit_of_measure_uri, URNP.validator, shapes_link))

        # Add the specific value type to value range invalid examples
        invalid_graph.add((invalid_value_range_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (
                invalid_value_range_result_bnode,
                RDF.value,
                Literal("-1.11", datatype=XSD.float),
            )
        )
        invalid_graph.add(
            (
                invalid_value_range_uri,
                SOSA.hasSimpleResult,
                Literal("-1.11", datatype=XSD.float),
            )
        )

        # Add unit of measure invalid examples in invalid_graph
        invalid_unit_of_measure_uri = URIRef(
            "urn:test:"
            + properties_collection_file_path
            + ":invalid:"
            + property_label_file_path
            + ":unit-of-measure"
        )

        invalid_graph.add((invalid_unit_of_measure_uri, RDF.type, TERN.Observation))
        invalid_graph.add(
            (invalid_unit_of_measure_uri, VOID.inDataset, invalid_in_dataset)
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_uri,
                RDFS.comment,
                Literal("Invalid result unit of measure"),
            )
        )

        invalid_unit_of_measure_feature_of_interest_bnode = BNode()
        invalid_graph.add(
            (
                invalid_unit_of_measure_uri,
                SOSA.hasFeatureOfInterest,
                invalid_unit_of_measure_feature_of_interest_bnode,
            )
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_feature_of_interest_bnode,
                RDF.type,
                TERN.FeatureOfInterest,
            )
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_feature_of_interest_bnode,
                VOID.inDataset,
                invalid_in_dataset,
            )
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_feature_of_interest_bnode,
                TERN.featureType,
                URIRef(property_feature_type),
            )
        )

        invalid_unit_of_measure_result_bnode = BNode()
        invalid_graph.add(
            (
                invalid_unit_of_measure_uri,
                SOSA.hasResult,
                invalid_unit_of_measure_result_bnode,
            )
        )
        invalid_graph.add((invalid_unit_of_measure_result_bnode, RDF.type, TERN.Value))
        invalid_graph.add((invalid_unit_of_measure_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (
                invalid_unit_of_measure_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_result_bnode,
                SOSA.isResultOf,
                invalid_unit_of_measure_uri,
            )
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_result_bnode,
                TERN.unit,
                URIRef("urn:fake:unit"),
            )
        )

        invalid_graph.add(
            (
                invalid_unit_of_measure_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )

        invalid_graph.add(
            (invalid_unit_of_measure_uri, SOSA.ObservableProperty, URIRef(property_uri))
        )
        invalid_graph.add(
            (invalid_unit_of_measure_uri, SOSA.phenomenonTime, invalid_phenomenon_time)
        )
        invalid_graph.add(
            (invalid_unit_of_measure_uri, SOSA.resultTime, invalid_result_time)
        )
        invalid_graph.add(
            (
                invalid_unit_of_measure_uri,
                SOSA.usedProcedure,
                URIRef(protocol_module_uri),
            )
        )
        invalid_graph.add(
            (invalid_unit_of_measure_uri, TERN.hasSiteVisit, URIRef("urn:test:site"))
        )

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                TERN.unit,
                URIRef(values_tbd),
            )
        )
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )

        # in value type
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                TERN.unit,
                URIRef(values_tbd),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )

        # in site visit
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                TERN.unit,
                URIRef(values_tbd),
            )
        )
        invalid_graph.add(
            (
                invalid_site_visit_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                TERN.unit,
                URIRef(values_tbd),
            )
        )
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                Literal("13.56", datatype=XSD.float),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                TERN.unit,
                URIRef(values_tbd),
            )
        )
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )

        # in datatype
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                RDF.value,
                Literal("3", datatype=XSD.integer),
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.Float))
        invalid_graph.add(
            (invalid_datatype_result_bnode, TERN.unit, URIRef(values_tbd))
        )
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasSimpleResult,
                Literal("3", datatype=XSD.integer),
            )
        )

        # Add valid examples
        valid_graph.add(
            (
                valid_example_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.Float))
        valid_graph.add(
            (valid_result_bnode, RDF.value, Literal("33.81", datatype=XSD.float))
        )
        valid_graph.add((valid_result_bnode, TERN.unit, URIRef(values_tbd)))

    elif URIRef(property_value_type) == TERN.Integer:
        shapes_graph.add((shapes_value_range_uri, SH.datatype, XSD.integer))

        # Add the specific value type to value range invalid examples
        invalid_graph.add((invalid_value_range_result_bnode, RDF.type, TERN.Integer))
        invalid_graph.add(
            (
                invalid_value_range_result_bnode,
                RDF.value,
                Literal("-1", datatype=XSD.integer),
            )
        )
        invalid_graph.add(
            (
                invalid_value_range_uri,
                SOSA.hasSimpleResult,
                Literal("-1", datatype=XSD.integer),
            )
        )

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                RDF.value,
                Literal("3", datatype=XSD.integer),
            )
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.Integer))
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                Literal("3", datatype=XSD.integer),
            )
        )

        # in value type
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                RDF.value,
                Literal("3", datatype=XSD.integer),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_uri,
                SOSA.hasSimpleResult,
                Literal("3", datatype=XSD.integer),
            )
        )

        # in site visit
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                RDF.value,
                Literal("3", datatype=XSD.integer),
            )
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.Integer))
        invalid_graph.add(
            (
                invalid_site_visit_uri,
                SOSA.hasSimpleResult,
                Literal("3", datatype=XSD.integer),
            )
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                Literal("3", datatype=XSD.integer),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.Integer))
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                Literal("2", datatype=XSD.integer),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                Literal("3", datatype=XSD.integer),
            )
        )
        invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.Integer))
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                Literal("3", datatype=XSD.integer),
            )
        )

        # in datatype
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                RDF.value,
                Literal("33.81", datatype=XSD.float),
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.Integer))
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasSimpleResult,
                Literal("33.81", datatype=XSD.float),
            )
        )

        # Add valid examples
        valid_graph.add(
            (
                valid_example_uri,
                SOSA.hasSimpleResult,
                Literal("3", datatype=XSD.integer),
            )
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.Integer))
        valid_graph.add(
            (valid_result_bnode, RDF.value, Literal("3", datatype=XSD.integer))
        )

    elif URIRef(property_value_type) == TERN.Text:
        shapes_graph.add((shapes_datatype_uri, SH.datatype, XSD.string))

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                RDF.value,
                Literal(values_tbd, datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.Text))
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                Literal(values_tbd, datatype=XSD.string),
            )
        )

        # in value type
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                RDF.value,
                Literal(values_tbd, datatype=XSD.string),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_uri,
                SOSA.hasSimpleResult,
                Literal(values_tbd, datatype=XSD.string),
            )
        )

        # in site visit
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                RDF.value,
                Literal(values_tbd, datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.Text))
        invalid_graph.add(
            (
                invalid_site_visit_uri,
                SOSA.hasSimpleResult,
                Literal(values_tbd, datatype=XSD.string),
            )
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                Literal(values_tbd, datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.Text))
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                Literal(values_tbd + " different", datatype=XSD.string),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                Literal(values_tbd, datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.Text))
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                Literal(values_tbd, datatype=XSD.string),
            )
        )

        # in datatype
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                RDF.value,
                Literal("1", datatype=XSD.integer),
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.Text))
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasSimpleResult,
                Literal("1", datatype=XSD.integer),
            )
        )

        # Add valid examples
        valid_graph.add(
            (
                valid_example_uri,
                SOSA.hasSimpleResult,
                Literal(values_tbd, datatype=XSD.string),
            )
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.Text))
        valid_graph.add(
            (valid_result_bnode, RDF.value, Literal(values_tbd, datatype=XSD.string))
        )

    elif URIRef(property_value_type) == TERN.Boolean:
        shapes_graph.add((shapes_datatype_uri, SH.datatype, XSD.boolean))

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                RDF.value,
                Literal(True, datatype=XSD.boolean),
            )
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.Boolean))
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                Literal(True, datatype=XSD.boolean),
            )
        )

        # in value type
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                RDF.value,
                Literal(True, datatype=XSD.boolean),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_uri,
                SOSA.hasSimpleResult,
                Literal(True, datatype=XSD.boolean),
            )
        )

        # in site visit
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                RDF.value,
                Literal(True, datatype=XSD.boolean),
            )
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.Boolean))
        invalid_graph.add(
            (
                invalid_site_visit_uri,
                SOSA.hasSimpleResult,
                Literal(True, datatype=XSD.boolean),
            )
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                Literal(True, datatype=XSD.boolean),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.Boolean))
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                Literal(False, datatype=XSD.boolean),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                Literal(True, datatype=XSD.boolean),
            )
        )
        invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.Boolean))
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                Literal(True, datatype=XSD.boolean),
            )
        )

        # in datatype
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                RDF.value,
                Literal(True, datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.Boolean))
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasSimpleResult,
                Literal(True, datatype=XSD.string),
            )
        )

        # Add valid examples
        valid_graph.add(
            (
                valid_example_uri,
                SOSA.hasSimpleResult,
                Literal(True, datatype=XSD.boolean),
            )
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.Boolean))
        valid_graph.add(
            (valid_result_bnode, RDF.value, Literal(True, datatype=XSD.boolean))
        )

    elif URIRef(property_value_type) == TERN.Date:
        shapes_graph.add((shapes_datatype_uri, SH.datatype, XSD.date))

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                RDF.value,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.Date))
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )

        # in value type
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                RDF.value,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )

        # in site visit
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                RDF.value,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.Date))
        invalid_graph.add(
            (
                invalid_site_visit_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.Date))
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-27", datatype=XSD.date),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )
        invalid_graph.add((invalid_used_procedure_result_bnode, RDF.type, TERN.Date))
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )

        # in datatype
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                RDF.value,
                Literal("2022-09-28", datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.Date))
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-28", datatype=XSD.string),
            )
        )

        # Add valid examples
        valid_graph.add(
            (
                valid_example_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-28", datatype=XSD.date),
            )
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.Date))
        valid_graph.add(
            (valid_result_bnode, RDF.value, Literal("2022-09-28", datatype=XSD.date))
        )

    elif URIRef(property_value_type) == TERN.DateTime:
        shapes_graph.add((shapes_datatype_uri, SH.datatype, XSD.dateTime))

        # Append values to other invalid examples

        # in feature type
        invalid_graph.add(
            (
                invalid_feature_type_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )
        invalid_graph.add((invalid_feature_type_result_bnode, RDF.type, TERN.DateTime))
        invalid_graph.add(
            (
                invalid_feature_type_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )

        # in value type
        invalid_graph.add(
            (
                invalid_value_type_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )
        invalid_graph.add(
            (
                invalid_value_type_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )

        # in site visit
        invalid_graph.add(
            (
                invalid_site_visit_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )
        invalid_graph.add((invalid_site_visit_result_bnode, RDF.type, TERN.DateTime))
        invalid_graph.add(
            (
                invalid_site_visit_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )

        # in simple result
        invalid_graph.add(
            (
                invalid_simple_result_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )
        invalid_graph.add((invalid_simple_result_result_bnode, RDF.type, TERN.DateTime))
        invalid_graph.add(
            (
                invalid_simple_result_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T12:26:56", datatype=XSD.dateTime),
            )
        )

        # in used procedure
        invalid_graph.add(
            (
                invalid_used_procedure_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )
        invalid_graph.add(
            (invalid_used_procedure_result_bnode, RDF.type, TERN.DateTime)
        )
        invalid_graph.add(
            (
                invalid_used_procedure_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )

        # in datatype
        invalid_graph.add(
            (
                invalid_datatype_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.string),
            )
        )
        invalid_graph.add((invalid_datatype_result_bnode, RDF.type, TERN.DateTime))
        invalid_graph.add(
            (
                invalid_datatype_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T11:09:56", datatype=XSD.string),
            )
        )

        # Add valid examples
        valid_graph.add(
            (
                valid_example_uri,
                SOSA.hasSimpleResult,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )
        valid_graph.add((valid_result_bnode, RDF.type, TERN.DateTime))
        valid_graph.add(
            (
                valid_result_bnode,
                RDF.value,
                Literal("2022-09-13T11:09:56", datatype=XSD.dateTime),
            )
        )

    # serialize shapes_graph into shapes.ttl
    if serialize_shapes:
        shapes_file_path = Path(
            "shapes/" + properties_collection_file_path + "/" + property_label_file_path
        )

        shapes_file_path.mkdir(exist_ok=True)

        shapes_graph.serialize(
            "shapes/"
            + properties_collection_file_path
            + "/"
            + property_label_file_path
            + "/shapes.ttl"
        )

    if serialize_invalid:
        invalid_file_path = Path(
            "shapes/" + properties_collection_file_path + "/" + property_label_file_path
        )

        invalid_file_path.mkdir(exist_ok=True)

        invalid_graph.serialize(
            "shapes/"
            + properties_collection_file_path
            + "/"
            + property_label_file_path
            + "/invalid.ttl"
        )

    if serialize_valid:
        valid_file_path = Path(
            "shapes/" + properties_collection_file_path + "/" + property_label_file_path
        )

        valid_file_path.mkdir(exist_ok=True)

        valid_graph.serialize(
            "shapes/"
            + properties_collection_file_path
            + "/"
            + property_label_file_path
            + "/valid.ttl"
        )
