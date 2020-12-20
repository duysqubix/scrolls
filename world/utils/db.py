"""
utility functions related to queries things from internal
script databases (objdb, roomdb, zonedb, mobdb, etc...)
"""
import re
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.middlewares import CachingMiddleware
from evennia import GLOBAL_SCRIPTS, logger
from evennia.utils.dbserialize import deserialize

_RE_COMPARATOR_PATTERN = re.compile(r"(<[>=]?|>=?|!)")

DB = None


def cachedb_init(db=None):
    global DB
    DB = TinyDB(storage=CachingMiddleware(MemoryStorage))
    dbs = None
    if not db:
        dbs = {
            'mobdb': GLOBAL_SCRIPTS.mobdb.vnum,
            'objdb': GLOBAL_SCRIPTS.objdb.vnum,
            'zonedb': GLOBAL_SCRIPTS.zonedb.vnum,
            'roomdb': GLOBAL_SCRIPTS.roomdb.vnum
        }
    else:
        dbs = {db: GLOBAL_SCRIPTS.get(db).vnum}

    ## i am too lazy right now to make this more exact
    # drop the damn thing and recreate it.
    for name, db in dbs.items():
        if name in DB.tables():
            DB.drop_table(name)

        table = DB.table(name)
        for vnum, data in db.items():
            table.insert({'vnum': vnum, **data})


if not DB:
    cachedb_init()


def like(val, cmp):
    return cmp in val


def between(val, l, h):
    return l <= val <= h


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

    # must supply either or
    if not vnum and not kwargs:
        return None

    def make_query(key, value):
        if key == 'extra':
            k, v = value.split(' ')
            return Query()[key][k] == v

        if isinstance(value, str):
            matches = re.split(_RE_COMPARATOR_PATTERN, value)
            if matches and len(matches) > 1:
                matches = matches[1:]
                condition, value = matches
                value = int(value)
                if condition == ">=":
                    return Query()[key] >= value
                elif condition == ">":
                    return Query()[key] > value
                elif condition == "<=":
                    return Query()[key] <= value
                elif condition == "<":
                    return Query()[key] < value

            matches = value.split('-')
            if matches and len(matches) == 2:
                # between range
                low, high = matches
                try:
                    low, high = int(low), int(high)
                except ValueError:
                    return Query()

                return Query()[key].test(between, low, high)

            return Query()[key].test(like, value)

        elif isinstance(value, list):
            return Query()[key].any(value)

    if vnum:
        if vnum == 'all':
            records = db.all()
        else:
            try:
                vnum = int(vnum)
                records = db.search(Query().vnum == vnum)
            except ValueError:
                return []
    else:
        query = None
        for key, value in kwargs.items():
            if not query:
                query = make_query(key, value)
            else:
                query &= make_query(key, value)

        records = db.search(query)

    if return_keys:
        return [x['vnum'] for x in records]
    return records


def search_mobdb(vnum=None, db=None, return_keys=False, **kwargs):
    db = DB.table('mobdb')
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


def search_objdb(vnum=None, db=None, return_keys=False, **kwargs):
    db = DB.table('objdb')
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


def search_zonedb(vnum=None, db=None, return_keys=False, **kwargs):
    db = DB.table('zonedb')
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)


def search_roomdb(vnum=None, db=None, return_keys=False, **kwargs):
    db = DB.table('roomdb')
    return _search_db(db=db, vnum=vnum, return_keys=return_keys, **kwargs)
