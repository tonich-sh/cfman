
from shlex import quote

from ..compiler import compiler
from ..cmd import Cmd, LongOpt


class Hg(Cmd):
    __slots__ = ['_subcmd', '_subopts']

    def __init__(self):
        super(Hg, self).__init__('hg')
        self._subcmd = ''
        self._subopts = []

    def repository(self, repo_dir):
        self._opts.append(LongOpt('--repository', repo_dir))
        return self

    def cwd(self, dir):
        self._opts.append(LongOpt('--cwd', dir))
        return self

    def clone(self, src, dst):
        self._subcmd = 'clone'
        self._subopts = [src, dst]
        return self

    def pull(self, remote='default'):
        self._subcmd = 'pull'
        self._subopts = [remote]
        return self

    def push(self, remote='default'):
        self._subcmd = 'push'
        self._subopts = [remote]
        return self

    def update(self, rev='tip'):
        self._subcmd = 'update'
        self._subopts = [rev]
        return self

    # def archive(self, format, rev, out=None):
    #     self._subcmd = 'archive'
    #     self._subopts = [LongOpt('--format', format)]
    #     if out:
    #         self._subopts.append(Opt('-o', out))
    #     self._subopts.append(rev)
    #     return self


@compiler.when(Hg)
def compile_hg(compiler, cmd: Hg, ctx, state):

    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)

    state.opts.append(quote(cmd._subcmd))
    for opt in cmd._subopts:
        compiler(opt, ctx, state)
