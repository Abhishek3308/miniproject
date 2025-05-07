from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter()
def inr(value):
    try:
        value = float(value)
        return "₹%s" % intcomma(int(value))
    except:
        return value
