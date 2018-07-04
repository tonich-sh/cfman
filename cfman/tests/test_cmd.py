
from cfman.cmdbuilder import cmd
from cfman.cmdbuilder.compiler import compiler


def test_pipe():
    pipe = cmd.Pipe('test1', 'test2')
    s, params = compiler(pipe, None)
    assert s == 'test1 | test2'

    pipe = cmd.OutputRedirect('test1', 'test2')
    s, params = compiler(pipe, None)
    assert s == 'test1 > test2'

    pipe = cmd.OutputRedirectAppend('test1', 'test2')
    s, params = compiler(pipe, None)
    assert s == 'test1 >> test2'


def test_cmd():
    c = cmd.Cmd('echo', 'just string').redir('/tmp/test1')
    s, params = compiler(c, None)
    assert s == 'echo \'just string\' > /tmp/test1'
