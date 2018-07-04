
from .. import deb
from . import file


def packages(ctx, packages, update=False):
    to_install = []
    for pkg in packages:
        if not deb.installed(ctx, pkg):
            to_install.append(pkg)
    if to_install:
        deb.install(ctx, to_install, update=update)


def apt_key(ctx, fingerprint, filename=None, url=None):
    if not deb.apt_key_exists(ctx, fingerprint):
        deb.apt_key_add(ctx, fingerprint, filename=filename, url=url)


def apt_source(ctx, name, uri, distribution, *components):
    path = '/etc/apt/sources.list.d/%(name)s.list' % locals()
    components = ' '.join(components)
    source_line = 'deb %(uri)s %(distribution)s %(components)s\n' % locals()
    file(ctx, path=path, contents=source_line)
