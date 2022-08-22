
import io
import os
import hashlib

from urllib.parse import urlparse
from cfman.executor.context import Context
from cfman.joblib.file import exists, md5sum
from cfman.cmdbuilder.commands import file as _file


BLOCKSIZE = 4098


def directory(ctx, path, owner=None, group=None, mode=None):

    if not exists(ctx, path):
        ctx.run(_file.Mkdir(path).parents())

    # Ensure correct owner
    if owner is not None:
        ctx.run(_file.Chown(path, owner=owner, group=group))
    elif group is not None:
        ctx.run(_file.Chgrp(path, group=group))

    # Ensure correct mode
    if mode is not None:
        ctx.run(_file.Chmod(path, mode=mode))


# TODO: contents encoding
def file(ctx: Context, path=None, contents=None, source=None, url=None, md5=None,
         owner=None, group=None, mode=None):

    if path and not (contents or source or url):
        assert path
        if not exists(ctx, path):
            ctx.run(_file.Touch(path))

    elif url:
        if not path:
            path = os.path.basename(urlparse(url).path)

        if not exists(ctx, path) or md5 and md5sum(ctx, path) != md5:
            ctx.run(_file.Wget(url).output(path), warn=True)

    # 3) A local filename, or a content string, is specified
    else:
        if contents:
            buf = bytes(contents, 'UTF-8')
            sum = hashlib.md5(buf).hexdigest()
            if not exists(ctx, path) or md5sum(ctx, path) != sum:
                ctx.put(io.BytesIO(buf), remote=path)
        elif source:
            # Avoid reading the whole file into memory at once
            digest = hashlib.md5()
            with open(source, 'rb') as f:
                while True:
                    d = f.read(BLOCKSIZE)
                    if not d:
                        break
                    digest.update(d)
            sum = digest.hexdigest()
            if not exists(ctx, path) or md5sum(ctx, path) != sum:
                ctx.put(source, remote=path)

    # Ensure correct owner
    if owner is not None and owner:
        ctx.run(_file.Chown(path, owner=owner, group=group))
    elif group is not None and group:
        ctx.run(_file.Chgrp(path, group=group))

    # Ensure correct mode
    if mode is not None:
        ctx.run(_file.Chmod(path, mode=mode))
