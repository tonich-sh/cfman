
import os
import sys
import logging

from importlib import util
from argparse import ArgumentParser

from . import job
from .context import Local, Remote


logger = logging.getLogger(__name__)


class Program(object):

    def __init__(self):
        self._hosts = []
        self._jobs = []

    @classmethod
    def load_jobfile(cls):
        sys.path.insert(0, os.getcwd())
        spec = util.find_spec('jobfile')
        if not spec:
            logger.warning('no jobfile in current directory (spec)')
            return
        mod = util.module_from_spec(spec)
        if not mod:
            logger.warning('no jobfile in current directory (module)')
            return
        spec.loader.exec_module(mod)

    def run(self, args=None):
        self.load_jobfile()
        if args is None:
            args = sys.argv[1:]
        # global params
        global_opts, tail = self.parse_global_opts(*args)
        if global_opts.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        logger.debug('global_opts: {}'.format(global_opts))
        if global_opts.hosts is not None:
            self._hosts = map(lambda x: x.strip(), global_opts.hosts.split(','))
        # job params
        jobs_dict = self.parse_job_opts(*tail)
        for job_name, job_params in jobs_dict.items():
            _job = job.registry.get(job_name, None)
            if _job is None:
                raise Exception('job "{}" not found'.format(job_name))
            # TODO: parse job params here?
            self._jobs.append((_job, job_params))
        # TODO: context factory by host type (ssh://root@test, localhost)
        for _job, job_params in self._jobs:
            for host in self._hosts:
                if host == 'localhost':
                    ctx = Local()
                else:
                    ctx = Remote(host)
                _job(ctx, *job_params)

    @classmethod
    def parse_global_opts(cls, *args):
        parser = ArgumentParser()
        parser.add_argument('-H', '--hosts')
        parser.add_argument('-d', '--debug', action='store_true')
        return parser.parse_known_args(args)

    @classmethod
    def parse_job_opts(cls, *args):
        jobs = {}
        j = None
        head = []
        for param in args:
            if param in job.registry.keys():
                #  start new job
                j = []
                jobs[param] = j
                continue
            else:
                if j is not None:
                    j.append(param)
                else:
                    head.append(param)
        return jobs


program = Program()
