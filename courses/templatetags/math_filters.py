from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) * float(arg)
        except (ValueError, TypeError):
            return 0

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        try:
            return float(value) / float(arg)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) - float(arg)
        except (ValueError, TypeError):
            return 0

@register.filter
def add(value, arg):
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) + float(arg)
        except (ValueError, TypeError):
            return str(value) + str(arg)