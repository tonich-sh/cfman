
from cfman.joblib.user import user_exists, group_exists
from cfman.cmdbuilder.commands.user import Useradd

def user(ctx, name, **kwargs):
    if not user_exists(ctx, name):
        res = ctx.run(Useradd().name(name))
        assert res.ok



def group(ctx):
    raise NotImplementedError()