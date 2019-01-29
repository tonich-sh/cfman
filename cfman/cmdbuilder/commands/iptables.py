
from shlex import quote

from ..compiler import compiler
from ..cmd import Cmd, LongOpt, Opt, Subcommand, Prefix


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


class Rule(object):
    __slots__ = ['_proto', '_source', '_destination', '_jump']

    def __init__(self):
        self._proto = None
        self._source = None
        self._destination = None
        self._jump = None

    def proto(self, p):
        self._proto = LongOpt('--proto', p, delim=' ')
        return self

    def not_proto(self, p):
        self._proto = Prefix('!', LongOpt('--proto', p, delim=' '))
        return self

    def source(self, addr):
        self._source = LongOpt('--source', addr, delim=' ')
        return self

    def destination(self, addr):
        self._destination = LongOpt('--destination', addr, delim=' ')
        return self

    def jump(self, target):
        self._jump = LongOpt('--jump', target, delim=' ')
        return self

    @property
    def opts(self):
        _opts = filter(lambda x: x is not None, [getattr(self, opt) for opt in self.__slots__])
        return _opts


@compiler.when(Rule)
def compile_iptables_rule(compiler, rule: Rule, ctx, state):
    for opt in rule.opts:
        compiler(opt, ctx, state)


class IptablesCheck(Subcommand):
    __slots__ = ['_rule']

    def __init__(self, ipt):
        super(IptablesCheck, self).__init__('--check', ipt)
        self._rule = None

    def rule(self, rule: Rule):
        self._rule = rule
        return self

    def chain(self, name):
        if name:
            self._opts.append(name)
        return self

    @property
    def opts(self):
        return self._opts + [self._rule]


class IptablesAppend(IptablesCheck):
    __slots__ = []

    def __init__(self, ipt):
        super(IptablesAppend, self).__init__(ipt)
        self.cmd = '--append'


class Iptables(Cmd):
    __slots__ = []

    def __init__(self, table=''):
        super(Iptables, self).__init__('iptables')
        if table:
            self._opts.append(Opt('-t', table))

    # Commands:

    def list(self, chain=''):
        return IptablesList(self).chain(chain)

    def check(self, chain, rule: Rule):
        return IptablesCheck(self).chain(chain).rule(rule)

    def new_chain(self, chain):
        self._opts.append(LongOpt('--new-chain', chain, delim=' '))
        return self

    def flush_chain(self, chain):
        self._opts.append(LongOpt('--flush', chain, delim=' '))
        return self

    def delete_chain(self, chain):
        self._opts.append(LongOpt('--delete-chain', chain, delim=' '))

    def append(self, chain, rule: Rule):
        return IptablesAppend(self).chain(chain).rule(rule)
