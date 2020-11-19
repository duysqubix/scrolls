"""
Default Scrolls object
All objects must inherit this class to work properly
"""
from world.characteristics import CHARACTERISTICS
import evennia
from world.utils.utils import is_obj, is_pc_npc
from world.conditions import ALL_CONDITIONS, Invisible, get_condition
from evennia import DefaultObject, GLOBAL_SCRIPTS


class Object(DefaultObject):
    """
    This is the root typeclass object, implementing an in-game Evennia
    game object, such as having a location, being able to be
    manipulated or looked at, etc. If you create a new typeclass, it
    must always inherit from this object (or any of the other objects
    in this file, since they all actually inherit from BaseObject, as
    seen in src.object.objects).

    The BaseObject class implements several hooks tying into the game
    engine. By re-implementing these hooks you can control the
    system. You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.


    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_before_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_after_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_after_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

    """

    __obj_type__ = ""
    __obj_specific_fields__ = {}
    __help_msg__ = ""

    # make it default quiet
    def move_to(
        self,
        destination,
        quiet=True,
        emit_to_obj=None,
        use_destination=True,
        to_none=False,
        move_hooks=True,
        **kwargs,
    ):
        super().move_to(destination, quiet, emit_to_obj, use_destination,
                        to_none, move_hooks, **kwargs)

    def basetype_setup(self):
        super().basetype_setup()
        self.locks.add(";".join(["call:false()", "puppet:false()"]))
        super().at_object_creation()
        self.db.name = ""
        self.db.sdesc = ""
        self.db.ldesc = ""
        self.db.edesc = ""  # extra description when specifically looked at
        self.db.adesc = ""
        self.db.type = None
        self.db.weight = 0
        self.db.cost = 0
        self.db.level = 0
        self.db.applies = []
        self.db.tags = []
        self.db.extras = {}
        self.db.is_obj = True

        for field, value in self.__obj_specific_fields__.items():
            self.attributes.add(field, value)

    def obj_desc(self, ldesc=False):
        """ returns string of tags currently set on obj"""
        if not self.db.tags:  # list is empty
            if not ldesc:
                return self.db.sdesc
            else:
                return self.db.ldesc

        tags = ""
        if 'invis' in self.db.tags:
            tags += "(|Cinvis|n)"
        if 'cursed' in self.db.tags:
            tags += "(|rcursed|n)"
        if 'daedric' in self.db.tags:
            tags += "(|rda|Yed|rric|n)"

        if not ldesc:
            return tags + " " + self.db.sdesc
        return tags + " " + self.db.lsdesc

    def at_object_creation(self):
        """ 
        Construct contents on object based on obj vnum
        which caller sets the key == vnum
        """

        obj = GLOBAL_SCRIPTS.objdb.vnum[int(self.key)]
        keys_aliases = obj['key'].split()

        self.db.name = keys_aliases
        self.db.sdesc = obj['sdesc']
        self.db.ldesc = obj['ldesc']
        self.db.adesc = obj['adesc']
        self.db.edesc = obj['edesc']
        self.db.type = obj['type']
        self.db.weight = obj['weight']
        self.db.cost = obj['cost']
        self.db.level = obj['level']
        self.db.applies = obj['applies']
        self.db.tags = obj['tags']
        self.db.extra = obj['extra']

        # set special fields as local attributes to class
        # incase efield isn't found, it will replace with default
        # value as specified in __obj_specific_fields__
        for efield, evalue in self.__obj_specific_fields__.items():
            if efield in self.db.extra.keys():
                self.attributes.add(efield, self.db.extra[efield])
            else:
                self.attributes.add(efield, evalue)


def apply_obj_effects(ch, obj):
    """
    apply the loaded effects from obj onto ch
    """
    if not is_pc_npc(ch) or not is_obj(obj):
        return

    applies = list(obj.db.applies)
    if not applies:
        return
    for effect in applies:
        if len(effect) == 2:
            apply_type, mod = effect

            if apply_type in VALID_OBJ_APPLIES['attrs']:
                ch.attrs.modify_vital(apply_type, by=mod)

            elif apply_type in VALID_OBJ_APPLIES['stats']:
                ch.stats.modify_stat(apply_type, by=mod)

        if len(effect) == 3:
            condition, x, y = effect
            if condition in VALID_OBJ_APPLIES['conditions']:
                con = get_condition(condition)
                ch.conditions.add(con)


def remove_obj_effects(ch, obj):
    """
    remove the loaded effects from obj onto ch
    """
    if not is_pc_npc(ch) or not is_obj(obj):
        return

    applies = list(obj.db.applies)
    if not applies:
        return

    for effect in applies:
        if len(effect) == 2:
            apply_type, mod = effect
            if apply_type in VALID_OBJ_APPLIES['attrs']:
                ch.attrs.modify_vital(apply_type, by=-mod)

            elif apply_type in VALID_OBJ_APPLIES['stats']:
                ch.stats.modify_stat(apply_type, by=-mod)
        if len(effect) == 3:
            condition, x, y = effect
            if condition in VALID_OBJ_APPLIES['conditions']:
                con = get_condition(condition)
                ch.conditions.remove(con)


VALID_OBJ_TAGS = ('invis', 'cursed', 'quest_item', 'no_sell', 'daedric')

VALID_OBJ_APPLIES = {
    'attrs': ('health', 'magicka', 'carry', 'speed', 'stamina'),
    'stats': ('str', 'end', 'agi', 'int', 'wp', 'prc', 'prs', 'lck'),
    'conditions': tuple((x.__obj_name__ for x in ALL_CONDITIONS))
}
