
from cfman.cmdbuilder.commands import git
from cfman.cmdbuilder.compiler import compiler


def test_git_clone():
    cmd = git.Git().clone('/tmp/test')
    s, params = compiler(cmd, None)
    assert s == 'git clone /tmp/test ./'
