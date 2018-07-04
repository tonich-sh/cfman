
from .registry import registry


class CompileException(Exception):
    pass


class Compiler(object):

    def get_compiler(self, obj):
        cls = type(obj)
        for c in cls.mro():
            _compiler = registry.get(c, None)
            if _compiler is not None:
                return _compiler
        return None

    def when(self, cls):
        def reg(func):
            registry[cls] = func
            return func
        return reg

    def __call__(self, job, ctx, state=None):
        if state is None:
            state = State()
            self(job, ctx, state)
            return ' '.join(state.opts), state.params
        c = self.get_compiler(job)
        if callable(c):
            c(self, job, ctx, state)
        else:
            raise CompileException('compiler for type "{}" not found'.format(job))


class State(object):
    def __init__(self):
        self.opts = []
        self.params = []


compiler = Compiler()
