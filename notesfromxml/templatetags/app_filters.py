from django import template


register = template.Library()


@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})
