
from cfman.cmdbuilder.cmd import Cmd

class Getent(Cmd):
    __slots__ = []

    def __init__(self):
        super(Getent, self).__init__('getent')

    def group(self):
        self._opts.append('group')
        return self

    def passwd(self):
        self._opts.append('passwd')
        return self