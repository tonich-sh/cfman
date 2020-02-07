
from cfman.executor.context import Context
from cfman.cmdbuilder.commands import getent, file


def user_exists(ctx: Context, name) -> bool:
    res = ctx.run(getent.Getent().passwd().pipe(file.Grep('^{}:'.format(name))))
    return res.ok


def group_exists(ctx: Context, name) -> bool:
    res = ctx.run(getent.Getent().group().pipe(file.Grep('^{}:'.format(name))))
    return res.ok
