
from ..cmd import Cmd, Subcommand


class IpAddress(Subcommand):
    def __init__(self, ip):
        super(IpAddress, self).__init__('address', ip)


class Ip(Cmd):
    __slots__ = []

    def __init__(self):
        super(Ip, self).__init__('ip')
        self._opts.append('-o')

    def address(self):
        return IpAddress(self)
