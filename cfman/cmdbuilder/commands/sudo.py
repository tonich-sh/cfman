
from shlex import quote

from ..compiler import compiler
from ..cmd import Cmd, Opt


class Sudo(Cmd):
    __slots__ = ['_cmd']

    def __init__(self, user=None):
        super(Sudo, self).__init__('sudo')
        self._opts.append('-S')
        if user is not None:
            self._opts.append('-u')
            self._opts.append(user)

    def command(self, cmd: Cmd):
        self._cmd = cmd
        return self


@compiler.when(Sudo)
def compile_sudo(compiler, cmd: Sudo, ctx, state):

    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)

    if cmd._cmd:
        compiler(cmd._cmd, ctx, state)



class Su(Cmd):
    __slots__ = ['_user', '_cmd', '_login']

    def __init__(self, user):
        super(Su, self).__init__('su')
        self._user = user
        self._cmd = None
        self._login = False

    def shell(self, shell):
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

