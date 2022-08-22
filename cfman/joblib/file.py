
from ..executor.context import Context
from ..cmdbuilder.commands import common, file

FILE_TYPE_SYMLINK = 'symlink'


def exists(ctx: Context, path, file_type=None):
    if file_type is None:
        return ctx.run(common.Test().file_exists(path), warn=True).ok
    if file_type == FILE_TYPE_SYMLINK:
        return ctx.run(common.Test().symlink_exists(path), warn=True).ok


def contains(ctx: Context, filename, pattern, exact=False, case_sensitive=True):
    return ctx.run(file.Grep(pattern, path=filename).case(on=case_sensitive).regexp(on=not exact), warn=True).ok


def append(ctx: Context, filename, text):
    ctx.run(common.Echo(text).redir_append(filename))


def replace(ctx: Context, filename, before, after, limit=None, backup='.bak', flags=''):
    """Replace text in file by sed patterns."""
    ctx.run(file.Sed(before, after, filename))


def temp_dir(ctx: Context, template=None, cleanup=True):
    path = ctx.run(file.Mktemp(template).directory().tmpdir()).stdout.strip()
    return TempDir(path, ctx=ctx, cleanup=cleanup)


def temp_file(ctx: Context, cleanup=True):
    path = ctx.run(file.Mktemp().tmpdir()).stdout.strip()
    return TempDir(path, ctx=ctx, cleanup=cleanup)


def remove(ctx: Context, filename, recursive=False):
    c = file.Rm(filename)
    if recursive:
        c.recursive()
    return ctx.run(c)


def copy(ctx: Context, src, dst):
    c = file.Cp(src, dst)
    ctx.run(c)


def move(ctx: Context, src, dst):
    c = file.Mv(src, dst)
    ctx.run(c)


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
