from functions import sparql_query
from settings import dawe_endpoint, tern_endpoint

import string

def get_op_collection_members(properties_collection_uri):

    q_get_op_collection_members = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    select ?properties where { 
        values ?s {$properties_collection_uri}
        ?s skos:member ?properties .
    }
    """

    q_get_op_collection_members = string.Template(
    q_get_op_collection_members
    ).substitute(properties_collection_uri=f"<{properties_collection_uri}>")

    op_collection_members = [
        i["properties"]["value"]
        for i in sparql_query(dawe_endpoint, q_get_op_collection_members)[
            "results"
        ]["bindings"]
    ]

    return op_collection_members

def get_op_meta_info(property_uri, method_uri):
    q_get_op_info = """
    select ?featureType ?valueType {
        values ?property_uri {$property_uri}
        values ?method_uri {$method_uri}
        ?s <urn:property:featureType> ?featureType ;
        <urn:property:valueType> ?valueType ;
        <urn:property:observableProperty> ?property_uri ;
        <urn:property:protocolModule> ?method_uri .
        }
    """

    q_get_op_info = string.Template(q_get_op_info).safe_substitute(
        property_uri=f"<{property_uri}>",
        method_uri=f"<{method_uri}>"
    )

    op_info_list = sparql_query(dawe_endpoint, q_get_op_info)["results"][
        "bindings"
    ]

    op_feature_type = op_info_list[0]["featureType"]["value"]
    op_value_type = op_info_list[0]["valueType"]["value"]

    return op_feature_type, op_value_type

def get_op_label(property_uri):
    q_get_op_label = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    select ?label {
    values ?property_uri {$property_uri}
    ?property_uri skos:prefLabel ?label .
    }
    """

    q_get_op_label = string.Template(q_get_op_label).substitute(
        property_uri=f"<{property_uri}>"
    )

    op_label = sparql_query(dawe_endpoint, q_get_op_label)["results"][
        "bindings"
    ][0]["label"]["value"]

    return op_label

def get_feature_type_label(feature_type_uri):
    q_get_feature_type_label = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    select ?label {
        values ?s {$feature_type_uri}
        ?s skos:prefLabel ?label .
    }
    """
    q_get_feature_type_label = string.Template(
        q_get_feature_type_label
    ).substitute(feature_type_uri=f"<{feature_type_uri}>")

    feature_type_label = sparql_query(
        tern_endpoint, q_get_feature_type_label
    )["results"]["bindings"][0]["label"]["value"].replace("-", " ")

    return feature_type_label