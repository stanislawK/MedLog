from django import template

register = template.Library()


@register.filter
def preventive(medicines):
    return medicines.filter(type="preventive")


@register.filter
def acute(medicines):
    return medicines.filter(type="acute")
