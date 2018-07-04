
from ..cmdbuilder.commands import common, file


def exists(ctx, path):
    return ctx.run(common.Test().file_exists(path), warn=True).ok


def contains(ctx, filename, text, exact=False, case_sensitive=True):
    return ctx.run(file.Grep(text, path=filename).case(on=case_sensitive).regexp(on=not exact), warn=True).ok


def append(ctx, filename, text):
    if not contains(ctx, filename, text):
        ctx.run(common.Echo(text).redir_append(filename))


def replace(ctx, filename, before, after, limit=None, backup='.bak', flags=''):
    if not contains(ctx, filename, before):
        return
    ctx.run(file.Sed(before, after, filename))


def temp_dir(ctx, template=None):
    path = ctx.run(file.Mktemp(template).directory().tmpdir()).stdout.strip()
    return TempDir(path, ctx=ctx)


def temp_file(ctx):
    path = ctx.run(file.Mktemp().tmpdir()).stdout.strip()
    return TempDir(path, ctx=ctx)


def remove(ctx, filename, recursive=False):
    c = file.Rm(filename)
    if recursive:
        c.recursive()
    return ctx.run(c)


def symlink(ctx, target, name):
    return ctx.run(file.Ln(target).symlink().name(name))


class TempDir(str):

    def __new__(cls, value, *args, **kwargs):
        s = super(TempDir, cls).__new__(cls, value)
        setattr(s, 'ctx', kwargs.get('ctx', None))
        return s

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.ctx.run(file.Rm(self).force().recursive())


def md5sum(ctx, path):
    res = ctx.run(file.BasePathCmd('md5sum', path), warn=True)
    if res.ok:
        return res.stdout.split(' ')[0]
    return ''

