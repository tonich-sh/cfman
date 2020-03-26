import re

from cfman.cmdbuilder.cmd import Cmd
from cfman.cmdbuilder.commands.file import Cat, Grep


def hostname(ctx):
    result = ctx.run(Cmd('hostname', '-f'))
    return result.stdout.strip().lower()


def memory_size(ctx):
    result = ctx.run(Cat('/proc/meminfo'))
    for l in result.stdout.strip().split("\n"):
        m = re.match(r'MemTotal:\s+([0-9]+).*', l)
        if m:
            return int(m.groups()[0])
    return 0
