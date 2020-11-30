"""
utility functions related to queries things from internal
script databases (objdb, roomdb, zonedb, mobdb, etc...)
"""

from typeclasses.objs.custom import CUSTOM_OBJS
from evennia import GLOBAL_SCRIPTS


def search_objdb(criteria, **kwargs):
    """
    the criteria can either be name or type of object
    first checks to see if it a valid object type before trying names

    The kwargs if for searching by 'extra' which is specific depending
    on object type. If the extras field are not existent, it will ignore the
    filter.

    ex:

    search_objdb('book', {'category': 'fiction'}) 
    # will return all objects of books that are in category of fiction.

    search_objdb('all') # returns all objects in database
    
    search_objdb('fire') # returns objects with the name fire
    """
    results = dict()
    objdb = GLOBAL_SCRIPTS.objdb.vnum

    if criteria == 'all':
        results.update(dict(objdb))
        return results

    use_type = True if criteria in CUSTOM_OBJS.keys() else False
    for vnum, data in objdb.items():

        if use_type and data['type'] == criteria:
            if not kwargs:
                results[vnum] = data
            elif kwargs.items() <= data['extra'].items():
                results[vnum] = data

        elif criteria in data['key']:
            results[vnum] = data
    return results