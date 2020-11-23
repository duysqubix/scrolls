from .rooms import Room


class RoomDefault(Room):
    __room_type__ = "default"


CUSTOM_ROOMS = {RoomDefault.__room_type__: RoomDefault}
