
import enum
import re
import os
from shlex import quote
from typing import List, Union

from ..compiler import compiler
from ..cmd import Cmd, LongOpt, Opt


# for support glob in file parameters
class ShellPath(object):
    __sots__ = '_path'

    def __init__(self, path):
        self._path = path


@compiler.when(ShellPath)
def compile_shell_path(compiler, cmd, ctx, state):
    path = cmd._path
    if path.startswith('*'):  # TODO: the same for "?" character ???
        path = '.' + os.sep + path
    if re.compile(r'[\n]', re.ASCII).search(path):
        raise Exception('Invalid chars in filename')
    # TODO: fix all invalid chars https://dwheeler.com/essays/fixing-unix-linux-filenames.html
    parts = map(lambda x: x.replace(' ', r'\ '), path.split(os.sep))
    state.opts.append(os.sep.join(parts))


class BasePathCmd(Cmd):
    __sots__ = '_path'

    def __init__(self, cmd, path):
        super(BasePathCmd, self).__init__(cmd)
        self._path = path
        self._opts = []

    @property
    def opts(self):
        return self._opts + [self._path]

    def path(self, path):
        self._path = path
        return self


class Cd(BasePathCmd):
    __slots__ = []

    def __init__(self, path):
        super(Cd, self).__init__('cd', path)


class Mkdir(BasePathCmd):
    __sots__ = []

    def __init__(self, path):
        super().__init__('mkdir', path)

    def parents(self):
        self._opts.append('-p')
        return self


class Mktemp(BasePathCmd):
    __slots__ = []

    def __init__(self, path=None):
        if path is None:
            path = 'XXXXX'
        super().__init__('mktemp', path)

    def directory(self):
        self._opts.append('--directory')
        return self

    def tmpdir(self, directory=None):
        if directory is None:
            self._opts.append('--tmpdir')
        else:
            self._opts.append(LongOpt('--tmpdir', directory))
        return self

    def template(self, template):
        self._path = template
        return self


class Stat(BasePathCmd):
    __sots__ = []

    def __init__(self, file_name):
        super().__init__('stat', file_name)
        self._opts = ['-t']


class Touch(BasePathCmd):
    __slots__ = []

    def __init__(self, file_name):
        super().__init__('touch', file_name)


class Cat(BasePathCmd):
    __slots__ = []

    def __init__(self, file_name: Union[str, List]):
        super().__init__('cat', file_name)

    @property
    def opts(self):
        return self._opts + self._path if isinstance(self._path, list) else [self._path]


class FindFileType(enum.Enum):
    BLOCK = 'b'  # block (buffered) special
    CHARACTER = 'c'  # character (unbuffered) special
    DIRECTORY = 'd'  # directory
    PIPE = 'p'  # named pipe (FIFO)
    FILE = 'f'  # regular file
    SYMLINK = 'l'  # symbolic link; this is never true if the -L option or the -follow option is in effect, unless the symbolic link is broken.  If you want to search for symbolic links when -L is in effect, use -xtype.
    SOCKET = 's'  # socket


class Find(BasePathCmd):
    __slots__ = []

    def __init__(self, path: str):
        super().__init__('find', path)

    @property
    def opts(self):
        return [self._path] + self._opts

    def name(self, pattern: str):
        self._opts.append(LongOpt('-name', pattern, delim=' '))
        return self

    def iname(self, pattern: str):
        self._opts.append(LongOpt('-iname', pattern, delim=' '))
        return self

    def type(self, ftype: Union[FindFileType, str]):
        self._opts.append(LongOpt('-type', ftype.value if isinstance(ftype, FindFileType) else ftype, delim=' '))
        return self


class RecursiveMixin:
    __slots__ = []

    def recursive(self):
        self._opts.append('-R')
        return self


class Chown(BasePathCmd, RecursiveMixin):
    __slots__ = []

    def __init__(self, path, owner, group=None):
        super().__init__('chown', path)
        if group is not None:
            self._opts.append('{}:{}'.format(owner, group))
        else:
            self._opts.append(owner)


class Chgrp(BasePathCmd, RecursiveMixin):
    __slots__ = []

    def __init__(self, path, group):
        super().__init__('chgrp', path)
        self._opts.append(group)


class Chmod(BasePathCmd, RecursiveMixin):
    __slots__ = []

    def __init__(self, path, mode):
        super().__init__('chmod', path)
        self._opts.append(mode)


class RecursiveMixinLower:
    __slots__ = []

    def recursive(self):
        self._opts.append('-r')
        return self


class Rm(BasePathCmd, RecursiveMixinLower):
    __slots__ = []

    def __init__(self, path):
        super().__init__('rm', ShellPath(path))

    def force(self):
        self._opts.append('-f')
        return self


class Mv(BasePathCmd):
    __slots__ = ['_dst']

    def __init__(self, path, dst):
        super().__init__('mv', path)
        self._dst = dst

    @property
    def opts(self):
        return self._opts + [self._path, self._dst]


class Cp(Mv, RecursiveMixinLower):
    __slots__ = []

    def __init__(self, path, dst):
        super().__init__(path, dst)
        self.cmd = 'cp'


class Ln(BasePathCmd):
    __slots__ = ['_name']

    def __init__(self, path, name=None):
        super().__init__('ln', path)
        if name is None:
            self._name = os.path.basename(path)

    def symlink(self):
        self._opts.append('-s')
        return self

    def name(self, name):
        self._name = name
        return self

    @property
    def opts(self):
        return self._opts + [self._path] + [self._name]


class Wget(Cmd):

    __slots__ = ['_url', '_out']

    def __init__(self, url):
        super().__init__('wget')
        self._url = url
        self._out = None

    def output(self, path=None):
        self._out = path
        return self

    @property
    def opts(self):
        _opts = self._opts + [self._url]
        if self._out is not None:
            _opts.append('-O')
            _opts.append(self._out)
        return _opts


class Grep(BasePathCmd):
    __slots__ = ['_pat', '_regexp', '_case']

    def __init__(self, pattern, path=None):
        super().__init__('grep', path)
        self._pat = pattern
        self._regexp = False
        self._case = False

    def regexp(self, on=True):
        self._regexp = on
        return self

    def case(self, on=True):
        self._case = on
        return self

    @property
    def opts(self):
        _opts = self._opts
        if not self._case:
            _opts.append('-i')
        return _opts

    def pattern(self, pattern):
        self._pat = pattern
        return self

    def only_matching(self):
        self._opts.append('-o')
        return self


@compiler.when(Grep)
def compile_grep(compiler, cmd, ctx, state):
    """

    :param compile:
    :param cmd:
    :type cmd: Grep
    :param ctx:
    :param state:
    :return:
    """
    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)
    # pattern
    state.opts.append(quote(cmd._pat))
    # file/path
    if cmd._path:
        state.opts.append(quote(cmd._path))


class Sed(BasePathCmd):
    __slots__ = ['_pat', '_repl', '_case', '_limit']

    def __init__(self, pattern, replacement, path=None):
        super().__init__('sed', path)
        self._pat = pattern
        self._repl = replacement
        self._limit = None

    def pattern(self, pattern):
        self._pat = pattern
        return self

    def repalcement(self, replacement):
        self._repl = replacement
        return self

    # def limit(self, limit):
    #     self._limit = limit
    #     return self

    @property
    def opts(self):
        _opts = self._opts
        # if not self._path:
        #     _opts.append('-i')
        return _opts


@compiler.when(Sed)
def compile_sed(compiler, cmd, ctx, state):
    """

    :param compiler:
    :param cmd:
    :type cmd: Sed
    :param ctx:
    :param state:
    :return:
    """
    state.opts.append(quote(cmd.cmd))
    for opt in cmd.opts:
        compiler(opt, ctx, state)
    pattern = cmd._pat
    repl = cmd._repl
    for char in "/'":
        pattern = pattern.replace(char, r'\%s' % char)
        repl = repl.replace(char, r'\%s' % char)
    for char in "()":
        repl = repl.replace(char, r'\%s' % char)
    # if limit:
    #     limit = r'/%s/ ' % limit
    expr = 's/{}/{}/g'.format(pattern, repl)
    state.opts.append("'" + expr + "'")
    if cmd._path:
        state.opts.append('-i')
        state.opts.append(quote(cmd._path))


class Diff(Cmd):
    __slots__ = ['_files']

    def __init__(self):
        super().__init__('diff')
        self._files = []

    def unified(self, num=None):
        if num is None:
            self._opts.append('--unified')
        else:
            self._opts.append(LongOpt('--unified', num))
        return self

    def files(self, *args):
        self._files = list(args)
        return self

    @property
    def opts(self):
        return self._opts + self._files
