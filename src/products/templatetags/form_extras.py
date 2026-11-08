from django import template

register = template.Library()


@register.filter
def add_class(field, css):
    existing = field.field.widget.attrs.get("class", "")
    field.field.widget.attrs["class"] = (existing + " " + css).strip()
    return field


@register.filter
def attr(field, arg):
    """
    Usage: {{ field|attr:"placeholder=Write here" }}
    """
    key, _, val = arg.partition("=")
    if key:
        field.field.widget.attrs[key] = val
    return field
