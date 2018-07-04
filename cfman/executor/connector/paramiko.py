
import os
import select
import logging

from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.config import SSH_PORT

from . import BaseConnection


class ParamikoConnection(BaseConnection):

    def __init__(self, **kwargs):
        self._ssh = None  # type: SSHClient
        host = kwargs.get('host', None)
        if host:
            splitted = host.split('@')
            self.host = splitted.pop(-1)
            if splitted:
                self.user = splitted[-1]
        else:
            self.host = None
            self.user = 'root'
        self._port = SSH_PORT

    def connect(self):
        logging.getLogger('paramiko').setLevel(logging.ERROR)
        self._ssh = SSHClient()
        self._ssh.set_missing_host_key_policy(AutoAddPolicy())
        self._ssh.load_system_host_keys()
        self._ssh.connect(
            self.host,
            self._port,
            self.user
        )

    def close(self):
        pass

    def connected(self):
        pass

    def exec_command(self, cmd):
        transport = self._ssh.get_transport()
        ch = transport.open_session()
        ch.exec_command(cmd)

        stdin = ''
        stdout = ''
        stderr = ''
        size = 1024 * 1024
        # TODO: write stdin to channel
        while True:

            r, w, x = select.select([ch], [], [], 1)

            if len(r):
                data = ch.recv(size)
                while data:
                    stdout += data.decode()
                    data = ch.recv(size)
                    for line in data.decode().splitlines():
                        print(line.strip())

                data = ch.recv_stderr(size)
                while data:
                    stderr += data.decode()
                    data = ch.recv_stderr(size)
                    for line in data.decode().splitlines():
                        print(line.strip())

            if ch.exit_status_ready():
                break

        return stdin, stdout, stderr, ch.recv_exit_status()

    def put_file(self, local, remote):
        is_file_object = hasattr(local, 'seek') and callable(local.seek)
        sftp = self._ssh.open_sftp()
        if is_file_object:
            sftp.putfo(local, remote)
        else:
            sftp.put(local, remote)
        return remote

    # def fetch_file(self, remote, local):
    #     sftp = self._ssh.open_sftp()
    #     pass

    def put_dir(self, local_path, remote_path):
        assert os.path.isdir(local_path)
        sftp = self._ssh.open_sftp()
        if os.path.basename(local_path):
            strip = os.path.dirname(local_path)
        else:
            strip = os.path.dirname(os.path.dirname(local_path))

        remote_paths = []

        for context, dirs, files in os.walk(local_path):
            rcontext = context.replace(strip, '', 1)
            rcontext = rcontext.replace(os.sep, '/')
            rcontext = rcontext.lstrip('/')
            rcontext = os.path.join(remote_path, rcontext)

            exists = False
            try:
                s = sftp.lstat(rcontext)
                exists = True
            except FileNotFoundError:
                pass

            if not exists:
                sftp.mkdir(rcontext)

            for d in dirs:
                n = os.path.join(rcontext, d)
                exists = False
                try:
                    s = sftp.lstat(rcontext)
                    exists = True
                except FileNotFoundError:
                    pass
                if not exists:
                    sftp.mkdir(n)
            for f in files:
                local_path = os.path.join(context, f)
                n = os.path.join(rcontext, f)
                p = sftp.put(local_path, n)
                remote_paths.append(p)

        return remote_paths

    # def fetch_dir(self):
    #     pass