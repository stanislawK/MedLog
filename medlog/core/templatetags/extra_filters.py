from django import template

register = template.Library()


@register.filter
def preventive(medicines):
    return medicines.filter(type="preventive")


@register.filter
def preventive_matches(medicines, id):
    return medicines.filter(type="preventive", id=id)


@register.filter
def preventive_list(medicines):
    return ", ".join(
        [str(preventive) for preventive in medicines.filter(type="preventive")]
    )


@register.filter
def acute(medicines):
    return medicines.filter(type="acute")


@register.filter
def acute_matches(medicines, id):
    return medicines.filter(type="acute", id=id)


@register.filter
def acute_list(medicines):
    return ", ".join([str(acute) for acute in medicines.filter(type="acute")])
