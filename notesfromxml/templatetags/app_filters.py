from django import template


register = template.Library()


@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter(name='sort_queryset')
def sort_queryset(value, arg):
    """
    Sorts a queryset in the Django template.
    Example usage: 'tag.tagmap_set.all|sort_list:"document__document_name"'
    This filter returns "tag.tagmap_set.all" in alphabetical order of "document__document_name".
    :param value: The queryset that needs to be sorted.
    :param arg: The argument that the queryset will be sorted by.
    :return: An ordered Queryset in the template.
    """
    return value.order_by(arg)
