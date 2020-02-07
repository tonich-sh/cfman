

import re
from cfman.cmdbuilder.commands import ip

ipv4_re = re.compile(r'.*\s+inet\s+([0-9\.]+).*')


def ipv4(ctx):
    addresses = []
    result = ctx.run(ip.Ip().address())
    for line in result.stdout.split('\n'):
        m = ipv4_re.match(line)
        if m:
            addresses.append(m.groups()[0])
    return addresses
