"""
utility functions related to queries things from internal
script databases (objdb, roomdb, zonedb, mobdb, etc...)
"""
import re
from evennia import GLOBAL_SCRIPTS, logger
from evennia.utils.dbserialize import deserialize
from evennia.utils.utils import inherits_from, is_iter, make_iter
from typeclasses.objs.custom import CUSTOM_OBJS

_RE_COMPARATOR_PATTERN = re.compile(r"(<[>=]?|>=?|!)")


def _search_db(db, criteria=None, return_keys=False, **kwargs):
    """
    Searches database based on kwargs. Citeria matches on either
    'all' or vnum of target. The kwargs only return if a record
    in db matches all supplied kwargs.

    Args:
        criteria: string to represent vnum OR 'all'
        return_keys: only returns the vnums from the search
        kwargs: extra keywords that are used to filter down results

    
    Extra Field:
        Some entities contain a special attribute on their blueprint called the
        `extra` field. This field is notable on the objects, and vary between each
        custom type of object (book, equipment, weapon, etc...) there is a special 
        handle in this function that handles this. 

        # search books that are in the aldmerish language
        books = search_obj(type='book', extra="langauge aldmerish")

        # search containers that have 10 item capacity
        containers = search_obj(type='container', extra='limit 10')

    Notes:
        In Kwargs, you can add flavor to the values to represent an integer
        ex:
            search_*(level=0) # return all mobs level 0
            search_*(level=">0") # return all mobs level > 0

        # to get mobs between a range (level 5-10)
        results = search_mobs(db=search_mobs(level=">=5"), level="<=10")

        # to get objects that weight between 2-10lbs
        results = search_objs(db=search_objs(weight=">=2"), weight="<=10")


    Usage:
        search_mobdb(1) # returns mob vnum 1

        search_mobdb('puff') # all mobs with the key 'puff' or 'puff' in sdesc

        search_mobdb(key='dog', attack='bite') # all mobs with the key of dog and attack of bite

        search_mobdb('all') # returns all mobs in db
    """
    results = dict()
    db = db

    if not criteria and not kwargs:
        return None

    if criteria:
        # try to see if criteria is vnum
        try:
            vnum = int(criteria)
            mob = db.get(vnum, None)
            if not mob:
                return None

            results[vnum] = mob
            return results if not return_keys else list(results.keys())
        except:
            pass

        if criteria == 'all':
            results.update(dict(db))
            return results if not return_keys else list(results.keys())

    for vnum, data in db.items():
        if kwargs:
            success_matches = 0
            for kfield, kvalue in kwargs.items():
                dvalue = data.get(kfield, None)
                dtype = type(dvalue)
                if not kfield:
                    break

                # handle base list type
                if dtype is list:
                    kvalue = dtype(kvalue.split(' '))
                    matches = all([x in dvalue for x in kvalue])
                    if not matches:
                        break
                    # results[vnum] = data
                    success_matches += 1
                    continue

                #  handle int types and ">=, >"... syntax
                elif dtype is int:
                    matches = re.split(_RE_COMPARATOR_PATTERN, kvalue)
                    if matches and len(matches) > 1:
                        matches = matches[1:]
                        condition, value = matches
                        value = dtype(value)
                        if condition == ">=" and dvalue >= value:
                            success_matches += 1
                        elif condition == ">" and dvalue > value:
                            success_matches += 1
                        elif condition == "<=" and dvalue <= value:
                            success_matches += 1
                        elif condition == "<" and dvalue < value:
                            success_matches += 1
                        continue

                    else:
                        kvalue = dtype(
                            kvalue)  # cast to type of what dvalue is
                        if kvalue == dvalue:
                            # results[vnum] = data
                            success_matches += 1
                            continue

                # handle dict on extra special fields
                elif dtype is dict and kfield == 'extra':
                    key, value = kvalue.split(' ')
                    for k, v, in dvalue.items():
                        vtype = type(v)
                        if k == key and v == vtype(value):
                            success_matches += 1
                            continue

                # handle str types as well as the logical tags
                elif dtype is str:
                    kvalue = dtype(
                        kvalue).lower()  # cast to type of what dvalue is
                    if kvalue in dvalue.lower():
                        # results[vnum] = data
                        success_matches += 1
                        continue
                else:
                    logger.log_errmsg(f"not supported data type: {dtype}")
                    continue

            if success_matches == len(kwargs):
                results[vnum] = data

    return results if not return_keys else list(results.keys())


def search_mobdb(criteria=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.mobdb.vnum) if not db else db
    return _search_db(db=db,
                      criteria=criteria,
                      return_keys=return_keys,
                      **kwargs)


def search_objdb(criteria=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.objdb.vnum) if not db else db
    return _search_db(db=db,
                      criteria=criteria,
                      return_keys=return_keys,
                      **kwargs)


def search_zonedb(criteria=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.zonedb.vnum) if not db else db
    return _search_db(db=db,
                      criteria=criteria,
                      return_keys=return_keys,
                      **kwargs)


def search_roomdb(criteria=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.roomdb.vnum) if not db else db
    return _search_db(db=db,
                      criteria=criteria,
                      return_keys=return_keys,
                      **kwargs)


# def search_objdb(criteria, **kwargs):
#     """
#     the criteria can either be name or type of object
#     first checks to see if it a valid object type before trying names

#     The kwargs if for searching by 'extra' which is specific depending
#     on object type. If the extras field are not existent, it will ignore the
#     filter.

#     ex:

#     search_objdb('book', **{'category': 'fiction'})
#     # will return all objects of books that are in category of fiction.

#     search_objdb('all') # returns all objects in database

#     search_objdb('fire') # returns objects with the name fire
#     """
#     results = dict()
#     objdb = GLOBAL_SCRIPTS.objdb.vnum

#     # try to see if criteria is vnum
#     try:
#         vnum = int(criteria)
#         obj = objdb.get(vnum, None)
#         if not obj:
#             return None

#         results[vnum] = obj
#         return results
#     except:
#         pass

#     if criteria == 'all':
#         results.update(dict(objdb))
#         return results

#     use_type = True if criteria in CUSTOM_OBJS.keys() else False
#     for vnum, data in objdb.items():

#         if use_type and data['type'] == criteria:
#             if not kwargs:
#                 results[vnum] = data
#             elif kwargs.items() <= data['extra'].items():
#                 results[vnum] = data

#         elif criteria in data['key']:
#             results[vnum] = data
#     return results