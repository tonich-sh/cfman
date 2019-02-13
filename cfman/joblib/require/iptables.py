
from cfman.executor.context import Context

from cfman.joblib.iptables import has_chain, has_rule
from cfman.cmdbuilder.commands.iptables import Iptables, Rule


def chain(ctx: Context, name, table=''):
    if not has_chain(ctx, name, table):
        res = ctx.run(Iptables(table=table).new_chain(name))
        assert res.ok


def rule(ctx: Context, _chain, _rule: Rule, table=''):
    chain(ctx, _chain, table=table)
    if not has_rule(ctx, _chain, _rule, table=table):
        res = ctx.run(Iptables(table=table).append(_chain, _rule))
        assert res.ok


def rules(ctx: Context, _chain, _rules, table='', clean=True):
    chain(ctx, _chain, table=table)
    if clean:
        assert ctx.run(Iptables().flush_chain(_chain)).ok
    c = Iptables(table=table).append(_chain, _rules[0])
    for r in _rules[1:]:
        c = c._chain(Iptables(table=table).append(_chain, r))

    assert ctx.run(c).ok
