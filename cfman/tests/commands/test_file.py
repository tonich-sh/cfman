
from cfman.cmdbuilder.commands import file
from cfman.cmdbuilder.compiler import compiler
from cfman.executor.context import Local


def test_mkdir():
    mkdir = file.Mkdir('/tmp/test1')
    s, params = compiler(mkdir, None)
    assert s == 'mkdir /tmp/test1'

    mkdir = file.Mkdir('/tmp/test test')
    s, params = compiler(mkdir, None)
    assert s == 'mkdir \'/tmp/test test\''

    mkdir = file.Mkdir('/tmp/test\'s test')
    s, params = compiler(mkdir, None)
    assert s == 'mkdir \'/tmp/test\'"\'"\'s test\''


def test_mktemp():
    mktemp = file.Mktemp()
    s, params = compiler(mktemp, None)
    assert s == 'mktemp XXXXX'
    mktemp = file.Mktemp().directory().tmpdir()
    s, params = compiler(mktemp, None)
    assert s == 'mktemp --directory --tmpdir XXXXX'


def test_cd():
    cd = file.Cd('/tmp')
    s, params = compiler(cd, None)
    assert s == 'cd /tmp'


def test_stat():
    stat = file.Stat('/tmp/test1')
    s, params = compiler(stat, None)
    assert s == 'stat -t /tmp/test1'


def test_chown():
    chown = file.Chown('/tmp/test1', 'user', 'user').recursive()
    s, params = compiler(chown, None)
    assert s == 'chown user:user -R /tmp/test1'


def test_grep():
    grep = file.Grep('test')
    s, params = compiler(grep, None)
    assert s == 'grep -i test'


def test_sed():
    grep = file.Sed('test1', 'test2', '/tmp/test1')
    s, params = compiler(grep, None)
    assert s == 'sed \'s/test1/test2/g\' -i /tmp/test1'
