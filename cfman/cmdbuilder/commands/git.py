
from shlex import quote

from ..compiler import compiler
from ..cmd import Cmd, LongOpt, Opt


class Git(Cmd):
    __slots__ = ['_subcmd', '_subopts']

    def __init__(self):
        super(Git, self).__init__('git')
        self._subcmd = ''
        self._subopts = []

    def git_dir(self, gd):
        self._opts.append(LongOpt('--git-dir', gd))
        return self

    def work_tree(self, wt):
        self._opts.append(LongOpt('--work-tree', wt))
        return self

    def rev_parse(self, rev):
        self._subcmd = 'rev-parse'
        self._subopts = [rev]
        return self

    def archive(self, format, rev, out=None):
        self._subcmd = 'archive'
        self._subopts = [LongOpt('--format', format)]
        if out:
            self._subopts.append(Opt('-o', out))
        self._subopts.append(rev)
        return self


@compiler.when(Git)
def compile_git(compiler, cmd: Git, ctx, state):

    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)

    state.opts.append(quote(cmd._subcmd))
    for opt in cmd._subopts:
        compiler(opt, ctx, state)
