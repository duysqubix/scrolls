r"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/pi/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *
######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "scrolls"

TELNET_PORTS = [4040]

GLOBAL_SCRIPTS = {
    'mobdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for mob data'
    },
    'objdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for obj data'
    },
    'roomdb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for room data'
    },
    'zonedb': {
        'typeclass': 'typeclasses.scripts.EntityDB',
        'persistent': True,
        'desc': 'storage for zones'
    }
}

CMDSET_UNLOGGEDIN = "evennia.contrib.menu_login.UnloggedinCmdSet"
BASE_BATCHPROCESS_PATHS += ["resources"]

BASE_OBJECT_TYPECLASS = "typeclasses.objs.object.Object"
BASE_ROOM_TYPECLASS = "typeclasses.rooms.rooms.Room"

BOOK_JSON = "resources/books/book.json"

TIME_FACTOR = 10
TIME_GAME_EPOCH = 0
TIME_UNITS = {
    "sec": 1,
    "min": 60,
    "hour": 60 * 60,
    "day": 60 * 60 * 24,
    "month": 60 * 60 * 24 * 31,
    "year": 60 * 60 * 24 * 31 * 12,
}

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

try:
    # Created by the `evennia connections` wizard
    from .connection_settings import *
except ImportError:
    pass