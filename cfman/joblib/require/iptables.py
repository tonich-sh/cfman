
from cfman.executor.context import Context

from cfman.joblib.iptables import has_chain
from cfman.cmdbuilder.commands.iptables import Iptables


def chain(ctx: Context, name, table=''):
    if not has_chain(ctx, name, table):
        res = ctx.run(Iptables(table=table).new_chain(name))
        assert res.ok
