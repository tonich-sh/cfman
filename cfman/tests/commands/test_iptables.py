
from cfman.cmdbuilder.commands import iptables
from cfman.cmdbuilder.compiler import compiler


def test_iptables_list():
    cmd = iptables.Iptables().list('test111').numeric()
    s, params = compiler(cmd, None)
    assert s == 'iptables --numeric --list test111'


def test_iptables_check():
    rule = iptables.Rule().not_proto('tcp').source('192.168.1.1/24').jump('ACCEPT')
    cmd = iptables.Iptables().check('test111', rule)
    s, params = compiler(cmd, None)
    assert s == 'iptables --check test111 ! --proto tcp --source 192.168.1.1/24 --jump ACCEPT'


def test_iptables_append():
    rule = iptables.Rule().not_proto('tcp').source('192.168.1.1/24').jump('ACCEPT')
    cmd = iptables.Iptables().append('test111', rule)
    s, params = compiler(cmd, None)
    assert s == 'iptables --append test111 ! --proto tcp --source 192.168.1.1/24 --jump ACCEPT'
