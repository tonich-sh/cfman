
from cfman.cmdbuilder.cmd import Cmd, Opt


class GroupCmd(Cmd):
    __slots__ = ['_name']

    def __init__(self, cmd, name):
        super(GroupCmd, self).__init__(cmd)
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


class Useradd(UserCmd):
    __slots__ = []

    def __init__(self, name):
        super(Useradd, self).__init__('useradd', name)

    def create_home(self):
        self._opts.append(Opt('-m'))
        return self


class Usermod(UserCmd):
    __slots__ = []

    def __init__(self, name):
        super(Usermod, self).__init__('usermod', name)


class Userdel(Cmd):
    __slots__ = []

    def __init__(self, name):
        super(Userdel, self).__init__('userdel', name)

    def force(self):
        self._opts.append('-f')
        return self

    def remove(self):
        self._opts.append('-r')
        return self


class Groupadd(GroupCmd):
    __slots__ = []

    def __init__(self, name):
        super(Groupadd, self).__init__('groupadd', name)

    def gid(self, n):
        self._opts.append(Opt('-g', n))
        return self


class Groupmod(Cmd):
    pass


class Groupdel(Cmd):
    pass
