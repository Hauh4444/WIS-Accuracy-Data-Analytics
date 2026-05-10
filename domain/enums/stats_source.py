from enum import Enum, auto


class StatsSource(Enum):

    HISTORICAL = auto()
    CURRENT = auto()
    AGGREGATE = auto()