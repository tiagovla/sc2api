from enum import Enum


class BaseEnum(Enum):
    def __str__(self):
        return "{0}".format(self.value)


class TeamType(BaseEnum):
    ARRANGED = 0
    RANDOM = 1


class QueueID(BaseEnum):
    WOL1V1 = 1
    WOL2V2 = 2
    WOL3V3 = 3
    WOW4V4 = 4
    HOTS1V1 = 101
    HOTS2V2 = 102
    HOTS3V3 = 103
    HOTS4V4 = 104
    LOTV1V1 = 201
    LOTV2V2 = 202
    LOTV3V3 = 203
    LOTV4V4 = 204
    LOTVARCHON = 206


class Region(BaseEnum):
    US = 1
    EU = 2
    KR = 3
    CN = 5


class League(BaseEnum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    DIAMOND = 4
    MASTER = 5
    GRANDMASTER = 6
