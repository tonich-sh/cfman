
import os

from cfman.executor.context import Result
from cfman.cmdbuilder.commands import deb, file, gpg
from cfman.joblib import file as file_job


def installed(ctx, pkg):
    res = ctx.run(deb.Dpkg(pkg).status().pipe(file.Grep('Status:').case()))
    if 'installed' in res.stdout.strip().split(' '):
        return True
    return False


def install(ctx, packages, update=False):
    if update:
        ctx.run(deb.AptGet().update(), warn=True)
    ctx.run(deb.AptGet().install(*packages), warn=True)


def apt_key_exists(ctx, fingerprint):
    if not file_job.exists(ctx, '/etc/apt/trusted.gpg'):
        return False
    with file_job.temp_dir(ctx, template='fabtools-gpghome.XXXXXXXXXX') as tmp_dir:
        # Command extracted from apt-key source
        g = gpg.Gpg(
            '--ignore-time-conflict',
            '--no-options',
            '--no-default-keyring',
        ).keyring('/etc/apt/trusted.gpg').homedir(tmp_dir).fingerprint(fingerprint)
        res = ctx.run(g, warn=True)
        result = res.ok
    return result


def apt_key_add(ctx, fingerprint=None, filename=None, url=None, keyserver=None):
    g = gpg.Gpg(
        '--ignore-time-conflict',
        '--no-options',
        '--no-default-keyring',
    )
    res = None
    if fingerprint is None:
        if filename is not None:
            res = ctx.run(deb.AptKey().add(filename), warn=True, hide=True)
        elif url is not None:
            with file_job.temp_dir(ctx, 'fabtools-gpghome.XXXXXXXXXX') as tmp_dir:
                assert ctx.run(ctx, file.Wget(url).output(os.path.join(tmp_dir, 'key.gpg')), warn=True, hide=True).ok
                res = ctx.run(ctx, g.keyring(os.path.join(tmp_dir, 'key.gpg')).homedir(tmp_dir).export(asc=True).pipe(deb.AptKey().add('-')), warn=True, hide=True)
        else:
            raise ValueError(
                'Either filename, url or keyid must be provided as argument')
    else:
        if filename is not None:
            res = ctx.run(deb.AptKey().add(filename), warn=True, hide=True)
        elif url is not None:
            with file_job.temp_dir(ctx, 'fabtools-gpghome.XXXXXXXXXX') as tmp_dir:
                if file_job.exists(ctx, '/etc/apt/trusted.db'):
                    assert ctx.run(file.Chmod('/etc/apt/trusted.db', 'o=r')).ok
                assert ctx.run(file.Wget(url).output(os.path.join(tmp_dir, 'key.gpg')), warn=True, hide=True).ok
                res = ctx.run(g.keyring(os.path.join(tmp_dir, 'key.gpg')).homedir(tmp_dir).export(asc=True).pipe(deb.AptKey().add('-')), warn=True, hide=True)
        else:
            raise NotImplementedError()
            # keyserver_opt = '--keyserver %(keyserver)s' % locals() if keyserver is not None else ''
            # run(ctx, 'apt-key adv %(keyserver_opt)s --recv-keys %(keyid)s' % locals(), warn=True, hide=True)
    if res is None:
        res = Result('', 'internal error', 1)
    return res
