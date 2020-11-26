

from enum import Enum

from cfman.cmdbuilder.cmd import Cmd


class Database(Enum):
    PASSWD = 'passwd'
    SHADOW = 'shadow'
    GROUP = 'group'


class Getent(Cmd):
    __slots__ = []

    def __init__(self, database: Database, key: str = ''):
        super(Getent, self).__init__('getent')
        self._opts.append(database)
        if key:
            self._opts.append(key)
