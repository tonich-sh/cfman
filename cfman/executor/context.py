
import abc
import os
import pwd
import signal
import shlex
import logging
from subprocess import Popen, PIPE
from contextlib import contextmanager

from cfman.cmdbuilder.cmd import Cmd, CommandChain
from cfman.cmdbuilder.commands import sudo, file
from cfman.cmdbuilder.compiler import compiler
from cfman.executor.connector.paramiko import ParamikoConnection


logger = logging.getLogger(__name__)


class Result(object):

    # TODO: add exception parameter
    def __init__(self, stdout='', stderr='', return_code=0):
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code

    @property
    def ok(self):
        return self.return_code == 0


class TransferResult(object):

    def __init__(self, local, remote, orig_remote='', orig_local='', context=None):
        self.orig_remote = orig_remote
        self.remote = remote
        self.orig_local = orig_local
        self.local = local
        self.context = context


class Context(object):

    def __init__(self, host='localhost'):
        """
        :param host:
        """
        self.host = host
        self.command_chain = []

    def _get_current_user(self):
        raise NotImplementedError

    @property
    def user(self):
        return self._get_current_user()

    def _prepare_cmd(self, cmd: Cmd, **kwargs):
        rcmd = cmd
        if 'user' in kwargs:
            user = kwargs['user']
            del kwargs['user']
            if hasattr(self, 'user') and self.user != user:
                if self.user == 'root':
                    # su
                    # TODO: configure shell
                    rcmd = sudo.Su(user).shell('/bin/sh').command(cmd)
                else:
                    # TODO: use sudo
                    rcmd = sudo.Sudo(user).command(cmd)
                    pass
        for cc in self.command_chain:
            rcmd = CommandChain(cc, rcmd)
        return rcmd

    @contextmanager
    def cd(self, path):
        self.command_chain.append(file.Cd(path))
        yield path
        self.command_chain.pop()

    @abc.abstractmethod
    def run(self, cmd: Cmd, **kwargs) -> Result:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, local, remote, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, remote, local, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def belong(self):
        raise NotImplementedError


class Local(Context):

    def __init__(self):
        super(Local, self).__init__('localhost')
        self._cwd = None

    def _get_current_user(self):
        return pwd.getpwuid(os.getuid())[0]

    def lrun(self, cmd: Cmd):
        return Local.run(self, cmd)

    @contextmanager
    def cd(self, path):
        self._cwd = path
        yield path
        self._cwd = None

    def run(self, cmd: Cmd, **kwargs):
        rcmd = self._prepare_cmd(cmd, **kwargs)
        # TODO: make splitted
        c, params = compiler(rcmd, self)
        logger.debug('{host}: {cmd}'.format(host=self.host, cmd=c))
        # return ctx.run(c, **kwargs)
        process = Popen(
            shlex.split(c),
            # shell=True,
            # executable='/bin/sh',
            # env=env,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            cwd=self._cwd
        )
        exception = None
        stdout = ''
        stderr = ''
        while True:
            try:
                stdout, stderr = process.communicate()
                break
            except KeyboardInterrupt as e:
                process.send_signal(signal.SIGINT)
                exception = e
                break
            except BaseException as e:
                exception = e
                break
        return Result(stdout.decode(), stderr.decode(), process.returncode)


class Remote(Context):

    def __init__(self, host):
        super(Remote, self).__init__(host)
        self.connection = ParamikoConnection(host=host)
        self.connection.connect()

    def _get_current_user(self):
        return self.connection.user

    def put(self, local, remote, **kwargs):
        """
        Do transfer local file/dir to remote location
        :param ctx:
        :param local:
        :param remote:
        :return:
        """
        if isinstance(local, str) and os.path.isdir(local):
            paths = self.connection.put_dir(local, remote)
            return TransferResult(
                local,
                remote,
                orig_local='',
                orig_remote=remote,
                context=self
            )
        else:
            path = self.connection.put_file(local, remote)
            return TransferResult(
                local,
                remote,
                orig_local='',
                orig_remote=remote,
                context=self
            )

    def get(self, remote, local, **kwargs):
        """
        Do transfer local file/dir from remote location
        """
        import stat
        s = self.connection.stat(remote)
        if stat.S_ISDIR(s.st_mode):
            raise NotImplementedError()
        else:
            path = self.connection.fetch_file(remote, local)
            return TransferResult(
                local,
                remote,
                orig_local=local,
                orig_remote='',
                context=self
            )

    def run(self, cmd: Cmd, **kwargs):
        rcmd = self._prepare_cmd(cmd, **kwargs)
        c, params = compiler(rcmd, self)
        logger.debug('{host}: {cmd}'.format(host=self.host, cmd=c))
        stdin, stdout, stderr, returncode = self.connection.exec_command(c)
        return Result(stdout, stderr, returncode)
