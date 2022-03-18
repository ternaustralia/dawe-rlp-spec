from jinja2 import Template

requirement_template = Template(
    """

"""
)

index_requirement_template = Template(
    """===== {{ title }}
{% for file in files %}
include::{{ file }}[]
{% endfor %}
"""
)
