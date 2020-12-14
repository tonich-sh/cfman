
from cfman.cmdbuilder.cmd import Cmd
from cfman.cmdbuilder.commands import sudo
from cfman.cmdbuilder.compiler import compiler


def test_sudo():
    _sudo = sudo.Sudo('www-data').command(Cmd('echo', 'test test', ))
    s, params = compiler(_sudo, None)
    assert s == 'sudo -S -u www-data echo \'test test\''


def test_su():
    _su = sudo.Su('www-data').command(Cmd('echo', 'test test'))
    s, params = compiler(_su, None)
    assert s == 'su -c " echo \'test test\' " www-data'
    _su.shell('/bin/bash')
    s, params = compiler(_su, None)
    assert s == 'su -s /bin/bash -c " echo \'test test\' " www-data'