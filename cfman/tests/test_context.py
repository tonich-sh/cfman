
from cfman.cmdbuilder.cmd import Cmd

from cfman.executor.context import Local, Remote


def test_local():

    loc = Local()
    result = loc.run(Cmd('/bin/ls', '/'))
    assert 'bin' in str(result.stdout)


def test_remote():

    loc = Remote('deploy')
    result = loc.run(Cmd('ls', '/'))
    # TODO: enable check
    assert 'bin' in str(result.stdout)
