
import abc


class BaseConnection(object):

    def connect(self):
        pass

    def close(self):
        pass

    def connected(self):
        pass

    @abc.abstractmethod
    def exec_command(self, cmd):
        pass

    @abc.abstractmethod
    def put_file(self, local, remote):
        pass

    @abc.abstractmethod
    def fetch_file(self, remote, local):
        pass
