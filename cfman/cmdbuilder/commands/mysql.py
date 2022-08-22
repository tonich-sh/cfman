from ..cmd import Cmd, LongOpt


__all__ = ['Mysql']


class Mysql(Cmd):

    def __init__(self):
        super(Mysql, self).__init__('mysql')

    def execute(self, statement):
        # TODO: quote statement properly
        self._opts.append(LongOpt('--execute', statement))
        return self

    def silent(self):
        self._opts.append(LongOpt('--silent', None))
        return self
