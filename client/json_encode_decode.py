#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from json import dumps, loads, JSONEncoder
# from json import JSONDecoder
import pickle

class PythonObjectEncoder(JSONEncoder):
    """
    author: Raymond Hettinger
    Twitter: @raymondh
    """
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float,
                            bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}


def as_python_object(dct):
    """
    author: Raymond Hettinger
    Twitter: @raymondh
    """
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct
