from typing import Optional, List

from cfman.cmdbuilder.commands.user import Useradd, Groupadd, Usermod, Userdel
from cfman.executor.context import Context
from cfman.joblib.user import (
    user_exists, group_exists,
    get_group_data, get_user_data,
)


def user(
        ctx: Context, name: str, uid=None, home_dir=None,
        shell=None, gid=None, password_hash=None,
        groups: Optional[List] = None,
        uid_min=None,
    ):
    do = False
    if not user_exists(ctx, name):
        cmd = Useradd(name)
        if uid is not None:
            cmd.uid(uid)
        if home_dir is not None:
            cmd.home_dir(home_dir)
            cmd.create_home()
        if shell is not None:
            cmd.shell(shell)
        if gid is not None:
            cmd.group(gid)
        if password_hash is not None:
            cmd.password(password_hash)
        if groups is not None:
            cmd.groups(groups)
        if uid_min is not None:
            cmd = cmd.config().uid_min(uid_min)
        do = True
    else:
        """
        {'name': 'user',
        'password': 'x',
        'uid': '1000',
        'gid': '1000',
        'gecos': 'user,,,',
        'home_dir': '/home/user',
        'shell': '/bin/bash',
        'encrypted_password': '$6$O19cUGGsELOqR1rA$Y6Ujo35JwuP/WhslyjuV/JZLAIJDMsFoNun4jLTtE554wUdwEyvtOgYk.Iyu2EkTKNrdBq1g4y6H7xWaXfBB81',
        'last_change': '18359',
        'min_age': '0',
        'max_age': '99999',
        'warn_period': '7',
        'inactivity_period': '',
        'exp_date': '',
        'reserved': ''}
        """
        user_data = get_user_data(ctx, name)
        cmd = Usermod(name)
        if uid is not None and int(user_data.get('uid', 0)) != int(uid):
            cmd.uid(uid)
            do = True
        if gid is not None:
            if isinstance(gid, str) and gid.isnumeric():
                gid = int(gid)
            else:
                group_data = get_group_data(ctx, gid)
                if not group_data:
                    raise Exception(f'Group "{gid}" not found')
                gid = int(group_data['gid'])
            if int(user_data.get('gid', 0)) != gid:
                do = True
                cmd.group(gid)
        if groups is not None:
            cmd.groups(groups)
        if home_dir is not None and user_data.get('home_dir', None) != home_dir:
            do = True
            cmd.home_dir(home_dir).move_home()
        if shell is not None and user_data.get('shell', None) != shell:
            do = True
            cmd.shell(shell)
        if password_hash is not None and user_data.get('encrypted_password', None) != password_hash:
            do = True
            cmd.password(password_hash)
    if do:
        res = ctx.run(cmd)
        assert res.ok


def not_user(ctx, name: str, delete_home: bool=False, allow_system: bool=False, force: bool=False):
    if user_exists(ctx, name):
        user_data = get_user_data(ctx, name)
        uid = int(user_data.get('uid', 0))
        # TODO: load system uid range from /etc/login.defs
        if uid < 1000 and not allow_system:
            raise Exception('are not allowed to delete system user "{user}": call with allow_system=True'.format(user=name))
        cmd = Userdel(name)
        if force:
            cmd.force()
        if delete_home:
            cmd.remove()
        res = ctx.run(cmd)
        assert res.ok


def group(ctx, name, gid=None):
    if not group_exists(ctx, name):
        cmd = Groupadd(name)
        if gid is not None:
            cmd.gid(gid)
        res = ctx.run(cmd)
        assert res.ok
