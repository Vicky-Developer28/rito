from django import template
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def format_number(value):
    """Format numbers with K/M suffixes"""
    if value is None:
        return "0"
    
    try:
        value = int(value)
    except (ValueError, TypeError):
        return str(value)
    
    if value >= 1000000:
        return f'{value/1000000:.1f}M'
    elif value >= 1000:
        return f'{value/1000:.1f}K'
    return str(intcomma(value))

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        value = float(value)
        total = float(total)
    except (ValueError, TypeError):
        return 0
    
    if total == 0:
        return 0
    return round((value / total) * 100, 1)

@register.simple_tag
def system_health_indicator(health_score):
    """Generate health indicator HTML"""
    try:
        health_score = float(health_score)
    except (ValueError, TypeError):
        health_score = 0
    
    if health_score >= 90:
        color = 'green'
        icon = 'check_circle'
    elif health_score >= 70:
        color = 'yellow'
        icon = 'warning'
    else:
        color = 'red'
        icon = 'error'
    
    return format_html(
        '<div class="health-indicator health-{}">'
        '<span class="material-icons">{}</span>'
        '<span>{}%</span>'
        '</div>',
        color, icon, health_score
    )