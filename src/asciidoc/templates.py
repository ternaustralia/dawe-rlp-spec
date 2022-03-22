from jinja2 import Template

# pylint: disable=line-too-long
requirement_template = Template(
    """[#{{ local_name }}]
====== {{ req.label }}

[frame=none, cols="1,5"]
|===
|Property | Value

|Identifier | `{{ req.iri }}`
|Label | {{ req.label }}
|Definition | {{ req.definition }}
|Comment | {{ req.comment }}
{% if req.status == "http://purl.org/linked-data/registry#statusSubmitted" %}include::../../../statuses/submitted.adoc[]{% elif req.status == "http://purl.org/linked-data/registry#statusStable" %}include::../../../statuses/stable.adoc[]{% else %}include::../../../statuses/invalid.adoc[]{% endif %}
|Conformance Classes | {{ req.conformance_classes }}
|Source | {{ req.source }}
|Validators | {% for validator in req.validators %}link:{{ validator.url }}[`{{ validator.label }}`]{% endfor %}
|Examples | Valid: link:{{ req.examples.valid_url }}[`{{ req.examples.valid_label }}`]

Invalid: link:{{ req.examples.invalid_url }}[`{{ req.examples.invalid_label }}`]
|===

"""
)

index_requirement_template = Template(
    """===== {{ title }}
{% for file in files %}
include::{{ file }}[]
{% endfor %}
"""
)
