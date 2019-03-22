
from shlex import quote

from .common import Cmd
from ..compiler import compiler


class AptGet(Cmd):
    __slots__ = ['_pkgs']

    def __init__(self):
        super(AptGet, self).__init__('apt-get')
        self._opts = ['-y', '-q=2']
        self._pkgs = []

    @property
    def opts(self):
        return self._opts + self._pkgs

    def install(self, *pkgs):
        self._opts.append('install')
        self._opts += list(pkgs)
        return self

    def update(self):
        self._opts.append('update')
        return self


@compiler.when(AptGet)
def compile_pipe(compiler, cmd, ctx, state):
    """

    :param compiler:
    :param cmd:
    :type cmd: Pipe
    :param ctx:
    :param state:
    :return:
    """
    state.opts.append('DEBIAN_FRONTEND=noninteractive')
    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)


class Dpkg(Cmd):
    __slots__ = ['_pkg']

    def __init__(self, pkg):
        super(Dpkg, self).__init__('dpkg')
        self._pkg = pkg

    def status(self):
        self._opts.append('-s')
        return self

    @property
    def opts(self):
        return self._opts + [self._pkg]


class AptKey(Cmd):
    __slots__ = []

    def __init__(self):
        super(AptKey, self).__init__('apt-key')

    def add(self, src):
        self._opts += ['add', src]
        return self
