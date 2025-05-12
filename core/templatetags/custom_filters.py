from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get a dictionary item by key in a template"""
    if dictionary is None:
        return None
    return dictionary.get(key)