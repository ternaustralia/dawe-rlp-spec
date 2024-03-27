import requests
from requests.exceptions import HTTPError


class SPARQLQueryError(Exception):
    pass


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


def generate_op_shapes_folder(op_label):
    op_shapes_folder_path = (
        "-".join(op_label.split())
        .replace("--", "-")
        .replace("--", "-")
        .replace("(", "")
        .replace(")", "")
    )
    return op_shapes_folder_path


def generate_protocol_folder(protocol_label):
    protocol_folder_path = (
        "-".join(
            protocol_label.lower()
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
        .replace(",", "")
    )
    return protocol_folder_path


def generate_observation_comment(
    validation_type, example_type, data_type, protocol_label, value_type, op_label
):
    if validation_type == "invalid":
        if example_type == "datatype":
            return (
                "Invalid result - the datatype of the value of the result node must be `"
                + data_type
                + "`."
            )
        elif example_type == "featuretype":
            return "Invalid result - incorrect feature type."
        elif example_type == "simpleresult":
            return "Invalid result - The value in simple result must be same with that in the result node."
        elif example_type == "sitevisit":
            return "Invalid result - all observations must have a site vist."
        elif example_type == "usedprocedure":
            return (
                "Invalid result - the used procedure should be '"
                + protocol_label
                + "'."
            )
        elif example_type == "valuerange":
            return "Invalid result - value out of range"
        elif example_type == "valuetype":
            return (
                "Invalid result - the value of the result node must be `"
                + value_type
                + "`."
            )
        else:
            print("Example type is out of consideration, please update the script.")
    else:
        return "Valid result for observable property - " + op_label
