import logging
import typer
import requests
from requests.exceptions import HTTPError
import json
from rdflib.namespace import RDF, RDFS, VOID, XSD, SOSA, DCTERMS, PROV, TIME, SH
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.collection import Collection

app = typer.Typer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


@app.command()
def fetch(filename: str):
    errors = 0

    g = Graph()

    g.parse(filename)

    q = """
        select ?uri ?query ?endpoint {
            ?uri a <urn:class:Controlled> ;
            <urn:property:query> ?query ;
            <urn:property:sparqlEndpoint> ?endpoint .

        }
    """

    for shape in g.query(q).bindings:

        uri = shape["uri"]
        query = shape["query"]
        endpoint = shape["endpoint"]

        try:
            data = sparql_query(endpoint, query)

            sh_in_value = g.value(uri, SH["in"])
            list = Collection(g, sh_in_value)
            list.clear()

            for r in data["results"]["bindings"]:
                list.append(URIRef(r["values"]["value"]))

        except SPARQLQueryError as err:
            logger.error(str(err))
            logger.error("Skipping shape %s", str(shape["uri"]))
            errors += 1

            # We stop processing the current shape,
            # Go to the next item in the iterator.
            continue

    g.serialize(filename)

    if errors:
        logger.info(f"{errors} error occurred.")


if __name__ == "__main__":
    app()
