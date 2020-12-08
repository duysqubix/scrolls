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


def _search_db(db, vnum=None, return_keys=False, **kwargs):
    """
    Searches database based on kwargs. Citeria matches on either
    'all' or vnum of target. The kwargs only return if a record
    in db matches all supplied kwargs. 

    If vnum is used, it ignores kwargs, vice-versa

    vnum quick-hand search function

    Args:
        db:  dictionary representation of the database
        vnum: string to represent vnum OR 'all'
        return_keys: only returns the vnums from the search
        kwargs: extra keywords that are used to filter down results

    Returns:
        Dictionary of matched records in the form as specified in DEFAULT_*_STRUCT in globals.py


    Usage:
        search_mobdb(1) # returns mob vnum 1

        search_mobdb('puff') # all mobs with the key 'puff' or 'puff' in sdesc

        search_mobdb(key='dog', attack='bite') # all mobs with the key of dog and attack of bite

        # search for equipment that cost more than 100 coin and weigh less than 10
        objs = search_objdb(type='equipment', weight="<10", cost=">=100")

        # search for monsters that have the name 'dog' and between the levels of 10 and 15 (but not 10 or 15)
        mobs = search_mobdb(name='dog', level=">10")
        mobs = search_mobdb(db=mobs, level="<15")
        
        search_mobdb('all') # returns all mobs in db

    Extra Field - Special Parsing:
        Some typeclasses contain a special attribute on their blueprint called the
        `extra` field. This field is notable on the objects, and vary between each
        custom type of object (book, equipment, weapon, etc...) there is a special 
        handle in this function that handles this. 

        # search books that are in the aldmerish language
        books = search_objdb(type='book', extra="langauge aldmerish")

        # search containers that have 10 item capacity
        containers = search_objdb(type='container', extra='limit 10')

    Notes:
        In Kwargs, you can add flavor to the values to represent an integer
        ex:
            search_*(level=0) # return all mobs level 0
            search_*(level=">0") # return all mobs level > 0

        # to get mobs between a range (level 5-10)
        results = search_mobs(db=search_mobs(level=">=5"), level="<=10")

        # to get objects that weight between 2-10lbs
        results = search_objs(db=search_objs(weight=">=2"), weight="<=10")

    """
    results = dict()
    db = db

    # must supply either or
    if not vnum and not kwargs:
        return None

    if vnum:
        # try to see if vnum is a valid integer
        try:
            vnum = int(vnum)
            mob = db.get(vnum, None)
            if not mob:
                return None

            results[vnum] = mob
            return results if not return_keys else list(results.keys())
        except:
            pass

        # return everything in db
        if vnum == 'all':
            results.update(dict(db))
            return results if not return_keys else list(results.keys())

    for vnum, data in db.items():
        if kwargs:

            success_matches = 0  # uses a counting system to make sure a specific record matches on ALL supplied kwargs
            for kfield, kvalue in kwargs.items():
                dvalue = data.get(kfield, None)
                dtype = type(dvalue)
                if not kfield:
                    break

                # some extra parsing protocols for each
                # data type depending on what the datatype is for the value in data

                # handle base list type
                if dtype is list:
                    # allows matching like so
                    # "1 2 3" == [1,2,3]
                    kvalue = dtype(kvalue.split(' '))
                    matches = all([x in dvalue for x in kvalue])
                    if not matches:
                        break
                    success_matches += 1
                    continue

                #  parses int types and parses the custom logical operator tags
                # >=, >, <= <
                # currently only supports single operators.
                # This is invalid:
                #  x = "10<,15>=" or something like that, it expects the format
                # [operator][value]
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
                        # cast to type of what dvalue is, this case it is int
                        kvalue = dtype(kvalue)
                        if kvalue == dvalue:
                            # results[vnum] = data
                            success_matches += 1
                            continue

                # handle parsing of on extra fields
                # extra field on data is simply another dictionary
                # within the dictionary.
                # allows the following to match:
                #
                # "language aldmerish" == {'language': 'aldmerish'}
                elif dtype is dict and kfield == 'extra':
                    key, value = kvalue.split(' ')
                    for k, v, in dvalue.items():
                        vtype = type(v)
                        if k == key and v == vtype(value):
                            success_matches += 1
                            continue

                # handle str types
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

            # if the number of success_matches == len(kwargs)
            # then each iteration of kwargs.items() found match, meaning
            # this record passes, and is stored
            if success_matches == len(kwargs):
                results[vnum] = data

    # return results, or keys if specified.
    return results if not return_keys else list(results.keys())


def search_mobdb(vnum=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.mobdb.vnum) if not db else db
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


def search_objdb(vnum=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.objdb.vnum) if not db else db
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


def search_zonedb(vnum=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.zonedb.vnum) if not db else db
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


def search_roomdb(vnum=None, db=None, return_keys=False, **kwargs):
    db = deserialize(GLOBAL_SCRIPTS.roomdb.vnum) if not db else db
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


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