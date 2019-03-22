
from ..cmdbuilder.commands import common, file


def exists(ctx, path, file_type=None):
    if file_type is None:
        return ctx.run(common.Test().file_exists(path), warn=True).ok
    if file_type == 'symlink':
        return ctx.run(common.Test().symlink_exists(path), warn=True).ok


def contains(ctx, filename, text, exact=False, case_sensitive=True):
    return ctx.run(file.Grep(text, path=filename).case(on=case_sensitive).regexp(on=not exact), warn=True).ok


def append(ctx, filename, text):
    if not contains(ctx, filename, text):
        ctx.run(common.Echo(text).redir_append(filename))


def replace(ctx, filename, before, after, limit=None, backup='.bak', flags=''):
    if not contains(ctx, filename, before):
        return
    ctx.run(file.Sed(before, after, filename))


def temp_dir(ctx, template=None, cleanup=True):
    path = ctx.run(file.Mktemp(template).directory().tmpdir()).stdout.strip()
    return TempDir(path, ctx=ctx, cleanup=cleanup)


def temp_file(ctx, cleanup=True):
    path = ctx.run(file.Mktemp().tmpdir()).stdout.strip()
    return TempDir(path, ctx=ctx, cleanup=cleanup)


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
        setattr(s, 'cleanup', kwargs.get('cleanup', True))
        return s

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if self.cleanup:
            self.ctx.run(file.Rm(self).force().recursive())


def md5sum(ctx, path):
    res = ctx.run(file.BasePathCmd('md5sum', path), warn=True)
    if res.ok:
        return res.stdout.split(' ')[0]
    return ''


def files_is_different(ctx, *files):
    res = ctx.run(file.Diff().files(*files))
    return not res.ok
