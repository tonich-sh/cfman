
import copy

from enum import Enum
from pathlib import Path

from shlex import quote
from .compiler import compiler


@compiler.when(str)
def compile_str(compiler, cmd, ctx, state):
    state.opts.append(quote(cmd))


@compiler.when(Enum)
def compile_enum(compiler, cmd, ctx, state):
    state.opts.append(str(cmd.value))


@compiler.when(Path)
def compile_path(compiler, cmd, ctx, state):
    state.opts.append(str(cmd))


class Opt:
    __slots__ = ['_name', '_value', '_delim']

    def __init__(self, name, value=None, delim=''):
        self._name = name
        self._value = value
        self._delim = delim


@compiler.when(Opt)
def compile_opt(compiler, opt, ctx, state):
    if opt._value is None:
        state.opts.append('{}'.format(quote(opt._name)))
    else:
        state.opts.append('{}{}{}'.format(quote(opt._name), opt._delim, quote(str(opt._value))))


class LongOpt(Opt):
    __slots__ = []

    def __init__(self, name: str, value, delim='='):
        super().__init__(name, value, delim)


class Pipe:
    __slots__ = ['_from', '_to', '_redir']

    def __init__(self, _from, _to):
        self._from = _from
        self._to = _to
        self._redir = '|'


@compiler.when(Pipe)
def compile_pipe(compiler, cmd, ctx, state):
    """

    :param compiler:
    :param cmd:
    :type cmd: Pipe
    :param ctx:
    :param state:
    :return:
    """
    compiler(cmd._from, ctx, state)
    state.opts.append(cmd._redir)
    compiler(cmd._to, ctx, state)


class OutputRedirect(Pipe):
    __slots__ = []

    def __init__(self, _from, _to):
        super().__init__(_from, _to)
        self._redir = '>'


class OutputRedirectAppend(Pipe):
    __slots__ = []

    def __init__(self, _from, _to):
        super().__init__(_from, _to)
        self._redir = '>>'


class CommandChain:
    __slots__ = ['_left', '_right']

    def __init__(self, left, right):
        self._left = left
        self._right = right

    def _chain(self, cmd):
        return CommandChain(self, cmd)


@compiler.when(CommandChain)
def compile_command_chain(compiler, cmd, ctx, state):
    compiler(cmd._left, ctx, state)
    state.opts.append(';')
    compiler(cmd._right, ctx, state)


# TODO: metaclass with registry of additional methods and properties
class Cmd:
    __slots__ = ['_opts', 'cmd']

    def __init__(self, cmd, *args, **kwargs):
        self.cmd = cmd
        self._opts = list(args)

    @property
    def opts(self):
        return self._opts

    def redir(self, file_name):
        return OutputRedirect(self, file_name)

    def redir_append(self, file_name):
        return OutputRedirectAppend(self, file_name)

    def pipe(self, cmd):
        return Pipe(self, cmd)

    def _chain(self, cmd):
        return CommandChain(self, cmd)

    def _clone(self):
        return copy.copy(self)


@compiler.when(Cmd)
def compile_cmd(compiler, cmd, ctx, state):
    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)


class Subcommand(Cmd):
    __slots__ = ['_parent', '_global_opts']

    def __init__(self, cmd, parent):
        super().__init__(cmd)
        self._parent = parent
        self._global_opts = []


@compiler.when(Subcommand)
def compile_subcommand(compiler, cmd: Subcommand, ctx, state):
    compiler(cmd._parent, ctx, state)

    for opt in cmd._global_opts:
        compiler(opt, ctx, state)

    state.opts.append(quote(cmd.cmd))

    for opt in cmd.opts:
        compiler(opt, ctx, state)


class Prefix(object):
    __slots__ = ['_prefix', '_obj']

    def __init__(self, prefix, obj):
        self._prefix = prefix
        self._obj = obj


@compiler.when(Prefix)
def compile_prefix(compiler, prefix: Prefix, ctx, state):
    state.opts.append(prefix._prefix)
    compiler(prefix._obj, ctx, state)


class CommandWrap(Cmd):
    __slots__ = ['_cmd']

    def __init__(self, wrapper):
        super().__init__(wrapper)

    def command(self, cmd: Cmd):
        self._cmd = cmd
        return self


@compiler.when(CommandWrap)
def compile_command_wrap(compiler, cmd: CommandWrap, ctx, state):

    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)

    if cmd._cmd:
        compiler(cmd._cmd, ctx, state)
