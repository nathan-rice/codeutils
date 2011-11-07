'''
Created on Oct 4, 2011

@author: Administrator
'''

import collections
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import ColumnProperty

def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return None

def safe_bool(value):
    if value in ("True", "true", True):
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
    "BigInteger":safe_int
}

def tune_attributes_to_model(cls, **kwargs):
    for k in kwargs:
        classattr = getattr(cls, k, None)
        if isinstance(classattr, InstrumentedAttribute):
            if isinstance(classattr.property, RelationshipProperty) and \
               classattr.property.direction.name in ("ONETOMANY", "MANYTOMANY"):
                # This should be a non-string iterable.  If it is a scalar, wrap it up
                if not isinstance(kwargs[k], collections.Sequence) or \
                   isinstance(kwargs[k], basestring):
                    values = [kwargs[k]]
                else:
                    values = kwargs[k]
                ids = [int(v) for v in values if not getattr(v, "_sa_instance_state", None)]
                "set ids on object here"

def adjust_sqla_property(classattr, name, value):
    if isinstance(classattr.property, RelationshipProperty) and \
       classattr.property.direction.name in ("ONETOMANY", "MANYTOMANY"):
        # This should be a non-string iterable.  If it is a scalar, wrap it up
        if not isinstance(value, collections.Sequence) or \
           isinstance(value, basestring):
            values = [value]
        else:
            values = value

        ids = [int(v) for v in values if not getattr(v, "_sa_instance_state, None")]
    elif isinstance(classattr.property, ColumnProperty):
        # Columns are typed, make the data respect that
        return safe_value(classattr)(value)
    else:
        # Not sure why we'd get here
        return value
