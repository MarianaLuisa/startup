from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """Substitui underscores por espaços."""
    return value.replace('_', ' ')
