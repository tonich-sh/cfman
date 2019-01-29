
from cfman.executor import job
from cfman.executor.program import Program


def test_parse_global_opts():
    program = Program()
    opts, tail = program.parse_global_opts(*['--hosts', 'root@deploy,root@test'])
    assert opts.hosts == 'root@deploy,root@test'


def test_parse_job_opts():
    job.registry = {'job1': job.Job(lambda x: None), 'job2': job.Job(lambda x: None)}
    program = Program()
    opts = program.parse_job_opts(*['job1', '--env=dev', 'job2', '--env=prod'])
    assert opts == {'job1': ['--env=dev'], 'job2': ['--env=prod']}


def test_run_a_decorated_job():

    a = 5

    @job.job
    def test1(ctx):
        nonlocal a
        a = 10

    program = Program()
    program.run(['cfman.tests.test_program.test1'])
    assert a == 10
