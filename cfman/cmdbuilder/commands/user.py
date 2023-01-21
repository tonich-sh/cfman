
from cfman.cmdbuilder.cmd import Cmd, Opt, Subcommand
from cfman.cmdbuilder.compiler import compiler

class GroupCmd(Cmd):
    __slots__ = ['_name']

    def __init__(self, cmd, name):
        super().__init__(cmd)
        self._name = name

    def name(self, s):
        self._name = s
        return self

    @property
    def opts(self):
        return self._opts + [self._name]


class UserCmd(GroupCmd):
    __slots__ = []

    def group(self, g):
        self._opts.append(Opt('-g', g))
        return self

    def uid(self, n):
        self._opts.append(Opt('-u', n))
        return self

    def shell(self, s):
        self._opts.append(Opt('-s', s))
        return self

    def password(self, p):
        self._opts.append(Opt('-p', p))
        return self

    def home_dir(self, d):
        self._opts.append(Opt('-d', d))
        return self

    def groups(self, groups: list):
        self._opts.append(Opt('-G', ','.join(groups)))
        return self


class LoginDefs(Subcommand):
    __slots__ = []

    def __init__(self, parent):
        super().__init__(None, parent)

    def uid_min(self, min_uid: int):
        self._opts.append(Opt(f'-KUID_MIN={min_uid}'))
        return self


@compiler.when(LoginDefs)
def compile_login_defs(compiler, cmd: LoginDefs, ctx, state):
    compiler(cmd._parent, ctx, state)

    for opt in cmd.opts:
        compiler(opt, ctx, state)

    for opt in cmd._global_opts:
        compiler(opt, ctx, state)


class Useradd(UserCmd):
    __slots__ = []

    def __init__(self, name):
        super().__init__('useradd', name)

    def create_home(self):
        self._opts.append(Opt('-m'))
        return self

    def config(self):
        return LoginDefs(self)


class Usermod(UserCmd):
    __slots__ = []

    def __init__(self, name):
        super().__init__('usermod', name)

    def move_home(self):
        self._opts.append(Opt('-m'))
        return self


class Userdel(Cmd):
    __slots__ = []

    def __init__(self, name):
        super().__init__('userdel', name)

    def force(self):
        self._opts.append('-f')
        return self

    def remove(self):
        self._opts.append('-r')
        return self


class Groupadd(GroupCmd):
    __slots__ = []

    def __init__(self, name):
        super().__init__('groupadd', name)

    def gid(self, n):
        self._opts.append(Opt('-g', n))
        return self


class Groupmod(Cmd):

    def __init__(self, name):
        raise NotImplementedError


class Groupdel(Cmd):

    def __init__(self, name):
        raise NotImplementedError
