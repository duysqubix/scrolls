from enum import Enum


class Gender(Enum):

    Male = 'male'
    Female = 'female'
    NoGender = 'NoGender'


ALL_GENDERS = [Gender.Male, Gender.Female, Gender.NoGender]


def get_gender(name):
    for g in ALL_GENDERS:
        if g.value == str(name).lower():
            return g
    raise ValueError('invalid gender requested')


def is_male(caller):
    if not caller.is_pc or not caller.is_npc:
        return False
    if caller.attrs.gender.value == Gender.Male:
        return True
    return False


def is_female(caller):
    if not caller.is_pc or not caller.is_npc:
        return False
    if caller.attrs.gender.value == Gender.Female:
        return True
    return False


def is_nogender(caller):
    if not caller.is_pc or not caller.is_npc:
        return False
    if caller.attrs.gender.value == Gender.NoGender:
        return True
    return False