
from .file import BasePathCmd
from ..cmd import Cmd, LongOpt, Opt


class Rsync(BasePathCmd):
    __slots__ = ['_dst']

    def __init__(self, src, dst):
        super(Rsync, self).__init__('rsync', src)
        self._dst = dst

    @property
    def opts(self):
        return self._opts + [self._path, self._dst]

    def recursive(self):
        self._opts.append(LongOpt('--recursive', None))
        return self

    def archive(self):
        self._opts.append(LongOpt('--archive', None))
        return self

    def verbose(self):
        self._opts.append(LongOpt('--verbose', None))
        return self
