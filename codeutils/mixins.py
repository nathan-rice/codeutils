"""
Created on Sep 13, 2011

@author: Administrator
"""

from datetime import date, time, datetime
from misc import get_attributes


class InitMixin(object):

    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)
        super(InitMixin, self).__init__()

class ReprMixin(object):

    def _format(self, v):
        if isinstance(v, (basestring, date, time, datetime)):
            v = "'%s'" % v
            return v.encode("utf-8", errors="ignore")
        else:
            return v

    def __repr__(self):
        attribute_string = ", ".join("%s=%s" % (k[0], self._format(k[1])) for k in get_attributes(self).items())
        return "%s(%s)" % (type(self).__name__, attribute_string)
