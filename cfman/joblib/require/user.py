
from cfman.joblib.user import user_exists, group_exists
from cfman.cmdbuilder.commands.user import Useradd, Groupadd


def user(ctx, name, uid=None, home_dir=None, shell=None, gid=None, **kwargs):
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
        res = ctx.run(cmd)
        assert res.ok


def group(ctx, name, gid=None):
    if not user_exists(ctx, name):
        cmd = Groupadd(name)
        if gid is not None:
            cmd.gid(gid)
        res = ctx.run(cmd)
        assert res.ok
