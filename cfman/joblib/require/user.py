
from cfman.joblib.user import user_exists, group_exists, get_user_data
from cfman.cmdbuilder.commands.user import Useradd, Groupadd, Usermod


def user(ctx, name, uid=None, home_dir=None, shell=None, gid=None, password_hash=None, **kwargs):
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
        if gid is not None:
            if isinstance(gid, str) and gid.isnumeric():
                gid = int(gid)
            else:
                # TODO: load group data and extract numeric gid
                raise Exception('non numeric gid is not supported yet')
            if int(user_data.get('gid', 0)) != gid:
                cmd.group(gid)
        if home_dir is not None and user_data.get('home_dir', None) != home_dir:
            cmd.home_dir(home_dir)
        if shell is not None and user_data.get('shell', None) != shell:
            cmd.shell(shell)
        if password_hash is not None and user_data.get('encrypted_password', None) != password_hash:
            cmd.password(password_hash)
    res = ctx.run(cmd)
    assert res.ok


def group(ctx, name, gid=None):
    if not group_exists(ctx, name):
        cmd = Groupadd(name)
        if gid is not None:
            cmd.gid(gid)
        res = ctx.run(cmd)
        assert res.ok
