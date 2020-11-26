
from cfman.cmdbuilder.commands import getent
from cfman.cmdbuilder.compiler import compiler


def test_getent_passwd():
    db = getent.Database.PASSWD
    cmd = getent.Getent(db)
    s, params = compiler(cmd, None)
    assert s == 'getent passwd'


def test_getent_shadow():
    cmd = getent.Getent(getent.Database.SHADOW)
    s, params = compiler(cmd, None)
    assert s == 'getent shadow'


def test_getent_shadow_root():
    cmd = getent.Getent(getent.Database.SHADOW, 'root')
    s, params = compiler(cmd, None)
    assert s == 'getent shadow root'
