
import copy

from shlex import quote
from .compiler import compiler


class Opt(object):
    __slots__ = ['_name', '_value', '_delim']

    def __init__(self, name, value=None, delim=''):
        self._name = name
        self._value = value
        self._delim = delim


class LongOpt(Opt):
    __slots__ = []

    def __init__(self, name, value, delim='='):
        super(LongOpt, self).__init__(name, value, delim)


class Pipe(object):
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
        super(OutputRedirect, self).__init__(_from, _to)
        self._redir = '>'


class OutputRedirectAppend(Pipe):
    __slots__ = []

    def __init__(self, _from, _to):
        super(OutputRedirectAppend, self).__init__(_from, _to)
        self._redir = '>>'


class CommandChain(object):
    __slots__ = ['_left', '_right']

    def __init__(self, left, right):
        self._left = left
        self._right = right


@compiler.when(CommandChain)
def compile_str(compiler, cmd, ctx, state):
    compiler(cmd._left, ctx, state)
    state.opts.append(';')
    compiler(cmd._right, ctx, state)


# TODO: metaclass with registry of additional methods and properties
class Cmd(object):
    __slots__ = ('_opts', 'cmd')

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

    def _clone(self):
        return copy.copy(self)


class Subcommand(Cmd):
    __slots__ = ['_parent', '_global_opts']

    def __init__(self, cmd, parent):
        super(Subcommand, self).__init__(cmd)
        self._parent = parent
        self._global_opts = []


@compiler.when(str)
def compile_str(compiler, cmd, ctx, state):
    state.opts.append(quote(cmd))


@compiler.when(Cmd)
def compile_cmd(compiler, cmd, ctx, state):
    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)


@compiler.when(Subcommand)
def compile_git_subcommand(compiler, cmd: Subcommand, ctx, state):
    compiler(cmd._parent, ctx, state)

    for opt in cmd._global_opts:
        compiler(opt, ctx, state)

    state.opts.append(quote(cmd.cmd))

    for opt in cmd.opts:
        compiler(opt, ctx, state)


@compiler.when(Opt)
def compile_opt(compiler, opt, ctx, state):
    state.opts.append('{}{}{}'.format(quote(opt._name), opt._delim, quote(opt._value)))
