
# from shlex import quote

# from ..compiler import compiler
from ..cmd import Cmd, LongOpt, Opt
# from ..commands.file import BasePathCmd


class Tar(Cmd):
    __slots__ = []
    
    def __init__(self):
        super(Tar, self).__init__('tar')

    def file(self, f):
        self._opts.append(Opt('-f', f))
        return self

    def extract(self):
        self._opts.append('-x')
        return self

    def create(self):
        self._opts.append('-c')
        return self

    def gz(self):
        self._opts.append('-z')
        return self

    def cdir(self, d):
        self._opts.append(Opt('-C', d))
        return self

    def path(self, path):
        self._opts.append(path)
        return self
