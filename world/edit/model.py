import copy

from evennia.utils.dbserialize import deserialize


class _EditMode:
    __cname__ = ""
    __mode__ = ""
    __db__ = None
    __prompt__ = "(NI)"
    __default_struct__ = {'extras': {}}

    def __init__(self, caller, vnum):
        self.caller = caller
        self.vnum = vnum
        self.db = self.__db__
        self.prompt = self.__prompt__
        self.obj = None
        self.orig_obj = None

        # attempt to find vnum in objdb
        if self.vnum in self.db.vnum.keys():
            self.obj = deserialize(self.db.vnum[self.vnum])
            self.caller.msg("|rstart|n")
            # account for new fields added to default object builder
            for field, value in self.__default_struct__.items():
                if field not in self.obj.keys():
                    self.obj[field] = value

                # handle special case if value is type dict
                if field in self.obj.keys() and isinstance(value, dict):
                    for nfield, nvalue in value.items():
                        if not self.obj[field].get(nfield, None):
                            self.obj[field][nfield] = nvalue

            # if obj is a special type based on type, add those
            # extra fields here
            try:
                obj_type = self.obj['type']
                if obj_type in self.custom_objs.keys():
                    extra_fields = self.custom_objs[
                        obj_type].__specific_fields__

                    for efield, evalue in extra_fields.items():
                        if efield not in self.obj['extra'].keys():
                            self.obj['extra'][efield] = evalue
            except:
                caller.msg(
                    f"<WARNING> entering {self.__prompt__} mode and custom_objs is not set. If this is for zedit or medit, safely ignore"
                )

        else:
            self.caller.msg(
                f"creating new {self.__cname__} vnum: [{self.vnum}]")
            self.obj = copy.deepcopy(self.__default_struct__)

        self.init()
        self.orig_obj = copy.deepcopy(self.obj)

    @property
    def custom_objs(self):
        raise NotImplementedError("must return a valid list of custom_objs")

    def init(self):
        pass

    def save(self, override=False, bypass_checks=False):
        if (self.orig_obj != self.obj) or override:
            self.db.vnum[self.vnum] = self.obj
            self.caller.msg('mob saved')

    def summarize(self):
        raise NotImplementedError()