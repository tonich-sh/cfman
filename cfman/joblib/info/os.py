
import re

from cfman.cmdbuilder.cmd import Cmd
from cfman.cmdbuilder.commands import file as file_cmd


def distribution(ctx):
    result = ctx.run(file_cmd.Grep(r'^ID=', path='/etc/os-release').case(on=True))
    # print('stdout: "{}"'.format(result.stdout))
    if result.ok:
        m = re.match(r'ID=[\'"]?([^\'"]+)[\'"]?', result.stdout.split('\n', maxsplit=1)[0])
        if m:
            return m.groups()[0].lower()
    return 'unknown'


def version(ctx):
    result = ctx.run(file_cmd.Grep(r'^VERSION_ID=', path='/etc/os-release').case(on=True))
    if result.ok:
        m = re.match(r'VERSION_ID=[\'"]?([^\'"]+)[\'"]?', result.stdout.split('\n', maxsplit=1)[0])
        if m:
            return m.groups()[0].lower()
    return '0'
