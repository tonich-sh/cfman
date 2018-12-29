
import inspect
import logging

from argparse import ArgumentParser

# from urllib.parse import urlparse

logger = logging.getLogger(__name__)

registry = {}


class Job(object):

    def __init__(self, func):
        self.callable = func

    def __call__(self, ctx, *args, **kwargs):
        # parse job params
        parser = ArgumentParser()
        for param in self.get_function_params():
            parser.add_argument('--{}'.format(param))
        parsed_args = parser.parse_args(args)
        sig = inspect.signature(self.callable)
        params = []
        kwparams = {}
        for parameter in list(sig.parameters.values())[1:]:  # skip first parameter - context
            param = '{}'.format(parameter.name)
            param_value = getattr(parsed_args, param)
            if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                if param_value is None:
                    kwparams['{}'.format(parameter.name)] = parameter.default
                else:
                    kwparams['{}'.format(parameter.name)] = param_value
            else:
                params.append(param_value)
        # run callable
        self.callable(ctx, *params, **kwparams)

    def get_function_params(self):
        sig = inspect.signature(self.callable)
        params = []
        for parameter in list(sig.parameters.values())[1:]:  # skip first parameter - context
            params.append('{}'.format(parameter.name))
        return params


def job(f=None, name=None, module=None):

    def outer(func):
        nonlocal module, name
        j = Job(func)
        if name is None:
            name = func.__name__
        if module is None:
            module = func.__module__
        if module == 'global':
            module = ''
        if module:
            job_name = '{}.{}'.format(module, name)
        else:
            job_name = '{}'.format(name)
        registry[job_name] = j

        def deco(*args, **kwargs):
            return j(*args, **kwargs)

        return deco

    if callable(f):
        return outer(f)

    return outer
