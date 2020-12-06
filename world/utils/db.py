"""
utility functions related to queries things from internal
script databases (objdb, roomdb, zonedb, mobdb, etc...)
"""

from evennia import GLOBAL_SCRIPTS
from evennia.utils.dbserialize import dbserialize
from typeclasses.objs.custom import CUSTOM_OBJS


def search_mobdb(criteria, **kwargs):
    """
    the criteria can either be name or keyword present in the
    key or sdesc of mob.

    The kwargs is used to filter down results based on valid field

    ex:

    search_mobdb('puff') # all mobs with the key 'puff' or 'puff' in sdesc

    search_mobdb('dog', **{'attack': 'bite'})
    # all mobs with the name or keyof dog and the attack type of bite

    search_mobdb('all') # returns all mobs in db
    """
    results = dict()
    mobdb = GLOBAL_SCRIPTS.mobdb.vnum

    # try to see if criteria is vnum
    try:
        vnum = int(criteria)
        mob = mobdb.get(vnum, None)
        if not mob:
            return None

        results[vnum] = mob
        return results
    except:
        pass

    if criteria == 'all':
        results.update(dict(mobdb))
        return results

    for vnum, data in mobdb.items():
        if criteria in data['key'] or \
           criteria in data['sdesc']:
            results[vnum] = data

        elif not kwargs:
            continue

        for kfield, kvalue in kwargs.items():
            dvalue = data.get(kfield, None)
            if not kfield:
                continue

            if dvalue == kvalue:
                results[vnum] = data
                continue
    return results


def search_objdb(criteria, **kwargs):
    """
    the criteria can either be name or type of object
    first checks to see if it a valid object type before trying names

    The kwargs if for searching by 'extra' which is specific depending
    on object type. If the extras field are not existent, it will ignore the
    filter.

    ex:

    search_objdb('book', **{'category': 'fiction'}) 
    # will return all objects of books that are in category of fiction.

    search_objdb('all') # returns all objects in database
    
    search_objdb('fire') # returns objects with the name fire
    """
    results = dict()
    objdb = GLOBAL_SCRIPTS.objdb.vnum

    # try to see if criteria is vnum
    try:
        vnum = int(criteria)
        obj = objdb.get(vnum, None)
        if not obj:
            return None

        results[vnum] = obj
        return results
    except:
        pass

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