

from ..cmd import Cmd


class Scp(Cmd):
    __slots__ = []

    def __init__(self):
        super(Scp, self).__init__('scp')