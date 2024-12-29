# In yourapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def range_filter(value):
    return range(value)




    
@register.filter
def make_slides(value, chunk_size):
    """Splits a list into chunks of a specified size."""
    chunk_size = int(chunk_size)
    return [value[i:i + chunk_size] for i in range(0, len(value), chunk_size)]
    