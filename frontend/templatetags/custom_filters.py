from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split a string into a list using the provided delimiter
    Usage: {{ "a,b,c"|split:"," }}
    """
    return value.split(arg) 