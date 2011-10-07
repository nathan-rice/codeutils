'''
Created on Oct 4, 2011

@author: Administrator
'''

def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return None

def safe_bool(value):
    if value in ("True", True):
        return True
    else:
        return False

def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None

def safe_value(attr):
    type_ = type(attr.property.columns[0].type).__name__
    return _column_converters.get(type_, lambda x: x)

_column_converters = {
    "Integer":safe_int,
    "Float":safe_float,
    "Boolean":safe_bool,
}
