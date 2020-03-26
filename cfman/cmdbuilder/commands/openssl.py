
from ..cmd import Cmd, LongOpt, Opt, Subcommand


__all__ = ['Openssl']


class Req(Subcommand):
    """-subj "$subj" -newkey rsa:2048 -days $days -nodes -keyout server-key.pem > server-req.pem"""
    def __init__(self, parent):
        super(Req, self).__init__('req', parent)

    def subj(self, s):
        self._opts.append(Opt('-subj', s, ' '))
        return self

    def newkey(self, k):
        self._opts.append(Opt('-newkey', k, ' '))
        return self

    def days(self, days):
        self._opts.append(Opt('-days', days, ' '))
        return self

    def nodes(self):
        self._opts.append(Opt('-nodes'))
        return self

    def keyout(self, file_name):
        self._opts.append(Opt('-keyout', file_name, ' '))
        return self

    @property
    def opts(self):
        return self._opts


class Rsa(Subcommand):
    """-in server-key.pem -out server-key.pem"""
    def __init__(self, parent):
        super(Rsa, self).__init__('rsa', parent)

    def in_(self, file_name):
        self._opts.append(Opt('-in', file_name, ' '))
        return self

    def out(self, file_name):
        self._opts.append(Opt('-out', file_name, ' '))
        return self


class X509(Subcommand):
    """-req -in server-req.pem -days $days -CA ca-cert.pem -CAkey ca-key.pem -set_serial $serial > server-cert.pem"""
    def __init__(self, parent):
        super(X509, self).__init__('x509', parent)

    def req(self):
        self._opts.append(Opt('-req'))
        return self

    def in_(self, file_name):
        self._opts.append(Opt('-in', file_name, ' '))
        return self

    def days(self, days):
        self._opts.append(Opt('-days', days, ' '))
        return self

    def CA(self, file_name):
        self._opts.append(Opt('-CA', file_name, ' '))
        return self

    def CAkey(self, file_name):
        self._opts.append(Opt('-CAkey', file_name, ' '))
        return self

    def set_serial(self, serial):
        self._opts.append(Opt('-set_serial', serial, ' '))
        return self


class Openssl(Cmd):

    def __init__(self):
        super(Openssl, self).__init__('openssl')

    def req(self):
        return Req(self)

    def rsa(self):
        return Rsa(self)

    def x509(self):
        return X509(self)
