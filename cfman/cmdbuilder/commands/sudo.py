
from shlex import quote

from ..compiler import compiler
from ..cmd import Cmd, Opt, CommandWrap


class Sudo(CommandWrap):
    __slots__ = []

    def __init__(self, user=None):
        super(Sudo, self).__init__('sudo')
        self._opts.append('-S')
        if user is not None:
            self._opts.append('-u')
            self._opts.append(user)


class Su(CommandWrap):
    __slots__ = ['_user', '_cmd', '_login']

    def __init__(self, user: str):
        super(Su, self).__init__('su')
        self._user = user
        self._cmd = None
        self._login = False

    def shell(self, shell: str):
        self._opts.append('-s')
        self._opts.append(shell)
        return self

    def command(self, cmd: Cmd, login=False):
        self._login = login
        self._cmd = cmd
        return self


@compiler.when(Su)
def compile_su(compiler, cmd: Su, ctx, state):

    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)

    if cmd._cmd:
        state.opts.append('-c')
        state.opts.append('"')
        compiler(cmd._cmd, ctx, state)
        state.opts.append('"')

    if cmd._login:
        state.opts.append('-l')

    state.opts.append(quote(cmd._user))

