
from cfman.executor.context import Context

from cfman.cmdbuilder.commands.file import Grep
from cfman.cmdbuilder.commands.iptables import Iptables, Rule


def has_chain(ctx: Context, chain, table=''):
    res = ctx.run(Iptables(table=table).list().numeric().pipe(Grep('^Chain {}'.format(chain))))
    return res.ok


def has_rule(ctx: Context, chain, rule: Rule, table=''):
    res = ctx.run(Iptables(table=table).check(chain, rule))
    return res.ok
