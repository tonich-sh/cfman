
from cfman.cmdbuilder.cmd import Cmd, Opt


class GroupCmd(Cmd):
    __slots__ = ['_name']

    def __init__(self, cmd):
        super(GroupCmd, self).__init__(cmd)
        self._name = None

    def name(self, s):
        self._name = s
        return self

    @property
    def opts(self):
        return self._opts + [self._name]
    

class Useradd(GroupCmd):
    __slots__ = []

    def __init__(self):
        super(Useradd, self).__init__('useradd')
    
    def uid(self, n):
        self._opts.append(Opt('-u', n))
        return self
    
    def shell(self, s='/bin/false'):
        self._opts.append(Opt('-s', s))
        return self
    
    def group(self, g):
        self._opts.append(Opt('-g', g))
        return self
    
    def home_dir(self, d):
        self._opts.append(Opt('-d', d))
        return self


class Usermod(Cmd):
    pass


class Userdel(Cmd):
    pass


class Groupadd(GroupCmd):
    __slots__ = []

    def __init__(self):
        super(Groupadd, self).__init__('groupadd')

    def gid(self, n):
        self._opts.append(Opt('-g', n))
        return self


class Groupmod(Cmd):
    pass


class Groupdel(Cmd):
    pass