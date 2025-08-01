

import re

from cfman.cmdbuilder.commands import ip
from cfman.executor.context import Context

ipv4_re = re.compile(r'.*\s+inet\s+([0-9\.]+).*')


def ipv4(ctx: Context) -> list[str]:
    addresses = []
    result = ctx.run(ip.Ip().address())
    for line in result.stdout.split('\n'):
        m = ipv4_re.match(line)
        if m:
            addresses.append(m.groups()[0])
    return addresses


def route(ctx: Context) -> list[str]:
    routes = []
    result = ctx.run(ip.Ip().route())
    for line in result.stdout.split('\n'):
        routes.append(line)
    return routes
