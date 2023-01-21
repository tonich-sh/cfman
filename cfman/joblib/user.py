
from cfman.executor.context import Context
from cfman.cmdbuilder.commands import getent, file


def user_exists(ctx: Context, name: str) -> bool:
    res = ctx.run(getent.Getent(getent.Database.PASSWD).pipe(file.Grep('^{}:'.format(name))))
    return res.ok


def group_exists(ctx: Context, name: str) -> bool:
    res = ctx.run(getent.Getent(getent.Database.GROUP).pipe(file.Grep('^{}:'.format(name))))
    return res.ok


def get_user_data(ctx: Context, name: str) -> dict:
    res = ctx.run(getent.Getent(getent.Database.PASSWD, name))
    passwd_data = {}
    if res.ok:
        passwd_fields = res.stdout.strip().split(':')
        passwd_headers = ('name', 'password', 'uid', 'gid', 'gecos', 'home_dir', 'shell')
        passwd_data = dict(zip(passwd_headers, passwd_fields))
    shadow_data = {}
    res = ctx.run(getent.Getent(getent.Database.SHADOW, name))
    if res.ok:
        shadow_fields = res.stdout.strip().split(':')
        shadow_headers = (
            'name', 'encrypted_password', 'last_change',
            'min_age', 'max_age', 'warn_period',
            'inactivity_period', 'exp_date', 'reserved')
        shadow_data = dict(zip(shadow_headers, shadow_fields))
    passwd_data.update(shadow_data)
    return passwd_data


def get_group_data(ctx: Context, name: str) -> dict:
    res = ctx.run(getent.Getent(getent.Database.PASSWD, name))
    if res.ok:
        group_fields = res.stdout.strip().split(':')
        group_headers = ('name', 'password', 'gid', 'user_list')
        group_data = dict(zip(group_headers, group_fields))
        group_data['user_list'] = group_data['user_list'].split(',')
        return group_data
    return {}
