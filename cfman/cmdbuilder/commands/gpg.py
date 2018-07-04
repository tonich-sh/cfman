

from ..cmd import Cmd, LongOpt


class Gpg(Cmd):
    __slots__ = []
    
    def __init__(self, *args):
        super(Gpg, self).__init__('gpg', *args)

    def keyring(self, k):
        self._opts.append(LongOpt('--keyring', k, ' '))
        return self

    def homedir(self, dir):
        self._opts.append(LongOpt('--homedir', dir, ' '))
        return self

    def fingerprint(self, fp):
        self._opts.append(LongOpt('--fingerprint', fp, ' '))
        return self

    def export(self, asc=False):
        self._opts.append('--export')
        if asc:
            self._opts.append('-a')
        return self