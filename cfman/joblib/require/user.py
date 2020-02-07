
from cfman.joblib.user import user_exists, group_exists
from cfman.cmdbuilder.commands.user import Useradd


def user(ctx, name, uid=None, home_dir=None, shell=None, **kwargs):
    if not user_exists(ctx, name):
        cmd = Useradd().name(name)
        if uid is not None:
            cmd.uid(uid)
        if home_dir is not None:
            cmd.home_dir(home_dir)
        if shell is not None:
            cmd.shell(shell)
        res = ctx.run(cmd)
        assert res.ok


def group(ctx):
    raise NotImplementedError()
