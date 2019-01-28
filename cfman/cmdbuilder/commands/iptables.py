
from shlex import quote

from ..compiler import compiler
from ..cmd import Cmd, LongOpt, Opt, Subcommand


class IptablesCommand(Subcommand):
    __slots__ = ['_global_opts']

    def __init__(self, cmd, ipt):
        super(IptablesCommand, self).__init__(cmd, ipt)


class IptablesList(Subcommand):

    def __init__(self, ipt):
        super(IptablesList, self).__init__('--list', ipt)

    def numeric(self):
        self._global_opts.append('--numeric')
        return self

    def chain(self, name):
        if name:
            self._opts.append(name)
        return self


@compiler.when(IptablesCommand)
def compile_git_subcommand(compiler, cmd: IptablesCommand, ctx, state):
    compiler(cmd._parent, ctx, state)

    for opt in cmd._global_opts:
        compiler(opt, ctx, state)

    state.opts.append(quote(cmd.cmd))

    for opt in cmd.opts:
        compiler(opt, ctx, state)


class Rule(Cmd):
    __slots__ = []

    def __init__(self):
        super(Rule, self).__init__('')


class Iptables(Cmd):
    __slots__ = []

    def __init__(self, table=''):
        super(Iptables, self).__init__('iptables')
        if table:
            self._opts.append(Opt('-t', table))

    # Commands:

    def list(self, chain=''):
        return IptablesList(self).chain(chain)

    def check(self):
        self._opts.append('--check')
        return self

    def new_chain(self, chain):
        self._opts.append(LongOpt('--new-chain', chain))
        return self

    def flush_chain(self, chain):
        self._opts.append(LongOpt('--flush', chain))
        return self

    def delete_chain(self, chain):
        self._opts.append(LongOpt('--delete-chain', chain))
