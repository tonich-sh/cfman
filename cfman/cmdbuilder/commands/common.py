
from ..cmd import Cmd


class Test(Cmd):
    __sots__ = '_path'

    def __init__(self):
        super(Test, self).__init__('test')

    def file_exists(self, path):
        self._opts = ['-e', path]
        return self

    def symlink_exists(self, path):
        self._opts = ['-h', path]
        return self


class Echo(Cmd):
    __slots__ = []

    def __init__(self, s):
        super(Echo, self).__init__('echo')
        self._opts = [s]
