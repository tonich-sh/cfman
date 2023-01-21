
import abc
import copy
import logging
import os
import pwd
import shlex
import signal
from contextlib import contextmanager
from pathlib import PurePath
from subprocess import PIPE, Popen
from typing import List, Union

from cfman.cmdbuilder.cmd import Cmd, CommandChain, CommandWrap
from cfman.cmdbuilder.commands import file, sudo
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

    def __init__(self, **kwargs):
        """
        :param host:
        """
        self.host = kwargs.get('host', None)
        self.command_chain: List[Cmd] = []
        self.command_wrap: Union[CommandWrap, None] = None

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
        for cc in self.command_chain:
            rcmd = CommandChain(cc, rcmd)
        if self.command_wrap:
            rcmd = self.command_wrap.command(rcmd)
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

    @contextmanager
    def belong(self, user: str):
        if self.user != user:
            self.command_wrap = sudo.Su(user).shell('/bin/sh')
        # else:
        #     self.command_wrap = sudo.Sudo(user)
        yield self.command_wrap
        self.command_wrap = None


class Local(Context):

    def __init__(self):
        super(Local, self).__init__(host='localhost')
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
        stdout = ''
        stderr = ''
        while True:
            try:
                stdout, stderr = process.communicate()
                break
            except KeyboardInterrupt:
                process.send_signal(signal.SIGINT)
                break
            except BaseException:
                break
        warn = kwargs.get('warn', False)
        if warn and stderr:
            logger.warning(stderr.decode())
        return Result(stdout.decode(), stderr.decode(), process.returncode)

    def put(self, local, remote, **kwargs):
        """
        Do transfer of local file/dir to remote location
        :param ctx:
        :param local:
        :param remote:
        :return:
        """
        is_file_object = hasattr(local, 'seek') and callable(local.seek)

        if is_file_object:
            open(remote, 'wb').write(local.getvalue())
        else:
            self.run(file.Cp(local, remote).recursive())


class Remote(Context):

    def __init__(self, host, **kwargs):
        kw = copy.copy(kwargs)
        kw.update(host=host)
        super().__init__(**kw)
        self.connection = ParamikoConnection(**kw)
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
        if isinstance(local, (str, PurePath)) and os.path.isdir(local):
            self.connection.put_dir(str(local), str(remote))
            return TransferResult(
                local,
                remote,
                orig_local='',
                orig_remote=remote,
                context=self
            )
        else:
            if isinstance(local, PurePath):
                local = str(local)
            self.connection.put_file(local, str(remote))
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
            self.connection.fetch_file(remote, local)
            return TransferResult(
                local,
                remote,
                orig_local=local,
                orig_remote='',
                context=self
            )

    def run(self, cmd: Cmd, **kwargs):
        rcmd = self._prepare_cmd(cmd, **kwargs)
        c, _ = compiler(rcmd, self)
        logger.debug('{host}: {cmd}'.format(host=self.host, cmd=c))
        _, stdout, stderr, returncode = self.connection.exec_command(c)
        warn = kwargs.get('warn', False)
        if warn and stderr:
            logger.warning(stderr)
        return Result(stdout, stderr, returncode)
