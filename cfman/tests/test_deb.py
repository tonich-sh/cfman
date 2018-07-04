

from cfman.executor.context import Remote
from cfman.joblib import  deb


def test_installed():
    ctx = Remote('root@deploy')
    ret = deb.installed(ctx, 'libc6')
    assert ret
