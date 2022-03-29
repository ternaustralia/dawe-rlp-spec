from jinja2 import Template

query = Template("""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
select ?iri ?label {
    VALUES (?iri) {
        {% for item in items %}(<{{ item }}>) {% endfor %}
    }
    ?iri skos:prefLabel ?label .
}
ORDER BY ?label
""")
