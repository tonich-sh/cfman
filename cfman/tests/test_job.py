

from cfman.executor.job import Job, job, registry


def test_get_function_params():
    def func1(ctx, test1, test2=None):
        pass

    j = Job(func1)
    params = j.get_function_params()
    assert params == ['test1', 'test2']


def test_decorator():

    @job
    def test1(ctx):
        pass

    assert 'cfman.tests.test_job.test1' in registry
