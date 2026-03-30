from django import template

register = template.Library()


@register.filter
def in_set(value, collection):
    """Check if value is in a set/collection. Usage: {{ value|in_set:my_set }}"""
    return value in collection
