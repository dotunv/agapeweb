from django import template

register = template.Library()

@register.simple_tag
def query_transform(request_get, **kwargs):
    """
    Returns the URL-encoded querystring for the current page,
    updating the params with the key/value pairs from kwargs.
    """
    updated = request_get.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode() 