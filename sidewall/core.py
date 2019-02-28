'''
core.py: core object classes for Sidewall.

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import json as jsonlib

from .debug import log


# Classes
# .............................................................................

# if json is not None:
#     if '_stats' in json and 'total_count' in json['_stats']:
#         self._total_count = json['_stats']['total_count']
#     else:
#         raise DataMismatch('Missing value in Dimensions JSON')

class DimensionsCore(object):
    _attributes = []

    def __init__(self, json, creator = None):
        self._json_data = json          # A dict.
        self._searched = set()          # Attributes we have searched for.
        self._hash = None

        from .dimensions_cls import Dimensions
        if isinstance(creator, Dimensions):
            self._dimensions = creator
        elif isinstance(creator, DimensionsCore):
            self._dimensions = creator._dimensions

        try:
            self._update_attributes(json)
        except KeyError as err:
            raise DataMismatch('Incomplete response from Dimensions')


    def _update_attributes(self, json):
        '''Method stub for subclasses to override.'''
        pass


    def __getattr__(self, attr):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        # Make every attribute lookup use object.__getattribute__.
        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        if attr in objattr('_attributes'):
            existing_attrs = objattr('__dict__')
            if attr not in existing_attrs:
                if __debug__: log('setting "{}" on object {}', attr, id(self))
                json = objattr('_json_data')
                if attr in json:
                    value = self._json_data.get(attr)
                    set_objattr(attr, value)
                    return value
        return objattr(attr)


    def __getattribute__(self, attr):
        # Be careful not to invoke "self.x" b/c it causes infinite recursion.
        # Make every attribute lookup use object.__getattribute__.
        objattr = lambda attr: object.__getattribute__(self, attr)
        set_objattr = lambda attr, value: object.__setattr__(self, attr, value)

        if __debug__: log('looking up "{}" on object {}', attr, id(self))
        if not attr in objattr('_attributes'):
            raise AttributeError(attr)
        if not (objattr(attr) or attr in objattr('_searched')):
            if __debug__: log('"{}" not yet set on object {}', attr, id(self))
            # Attribute has no value and we haven't tried searching for it.
            # Whether we can search or not, we set the flag that we tried.
            searched = objattr('_searched')
            searched.add(attr)      # Warning: don't combine this w/ next line.
            set_objattr('_searched', searched)
            try:
                search_tmpl = objattr('_search_tmpl')
            except:
                if __debug__: log("no search template -- can't fill in values")
                pass
            else:
                dim_id = objattr('id')
                if dim_id:
                    dim = objattr('_dimensions')
                    search = object.__getattribute__(dim, 'record_search')
                    record_json = search(search_tmpl, dim_id)
                    objattr('_fill_record')(record_json)
                else:
                    if __debug__: log("missing id -- can't search for \"{}\"".format(attr))
        return objattr(attr)


    def __repr__(self):
        return "<DimensionsCore 0x{0:x}>".format(id(self))


    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and ordered(self) == ordered(other))


    def __ne__(self, other):
        return not self.__eq__(other)


    def __gt__(self, other):
        return not __le__(self, other)


    def __ge__(self, other):
        return not __lt__(self, other)


    def __lt__(self, other):
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id.lower() < other.id.lower()
        else:
            return repr(self) < repr(other)


    def __le__(self, other):
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id.lower() <= other.id.lower()
        else:
            return repr(self) <= repr(other)


    def __cmp__(self, other):
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return cmp(self.id.lower(), other.id.lower())
        else:
            return cmp(repr(self), repr(other))


    def __hash__(self):
        if self._hash:
            return self._hash
        if hasattr(self, 'id'):
            self._hash = hash(self.id)
        elif hasattr(self, '_json_data') and self._json_data:
            self._hash = hash(jsonlib.dumps(self._json_data))
        else:
            self._hash = hash(self)
        return self._hash
