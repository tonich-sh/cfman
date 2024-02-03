
import shlex

from ..cmd import Cmd
from ..compiler import compiler


class PsqlQuote:
    __slots__ = ('_value', )

    def __init__(self, value):
        self._value = value


@compiler.when(PsqlQuote)
def compile_enum(compiler, unquoted, ctx, state):
    state.opts.append(shlex.quote(unquoted._value).replace('"', r'\"'))


class Psql(Cmd):

    def __init__(self):
        super(Psql, self).__init__('psql')

    def command(self, statement):
        self._opts.append('--command')
        self._opts.append(PsqlQuote(statement))
        return self
