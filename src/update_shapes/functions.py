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