from django import template
from root import settings
from datetime import datetime

register = template.Library()


@register.filter
def replace_dash_with_dot(data):
    if not data:
        return ""
    return data.replace("-", ".")


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.filter
def convert_str_date(value):
    return str(datetime.strptime(value, '%Y-%m-%d').strftime('%d/%m/%Y'))