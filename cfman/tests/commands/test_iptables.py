
from cfman.cmdbuilder.commands import iptables
from cfman.cmdbuilder.compiler import compiler


def test_iptables_list():
    cmd = iptables.Iptables().list('test111').numeric()
    s, params = compiler(cmd, None)
    assert s == 'iptables --numeric --list test111'
