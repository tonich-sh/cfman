
import logging
import traceback

from typing import List

from cfman.cmdbuilder.commands import rabbitmq, file


logger = logging.getLogger(__name__)


def user(ctx, name, password, tags=None, perms=None):
    res = ctx.run(rabbitmq.RabbitmqCtl().list_users().pipe(file.Grep('^' + name + '\\s')))
    exists = res.ok

    if not exists:
        logger.warning('user {} not exists'.format(name))
        assert ctx.run(rabbitmq.RabbitmqCtl().add_user(name, password)).ok
    else:
        logger.warning('user {} already exists'.format(name))
        assert ctx.run(rabbitmq.RabbitmqCtl().change_password(name, password)).ok

    if isinstance(tags, (list, tuple)):
        assert ctx.run(rabbitmq.RabbitmqCtl().set_user_tags(name, list(tags))).ok

    if isinstance(perms, (list, tuple)):
        _perms = list(perms)
        try:
            if len(_perms) == 4:
                vhost = _perms.pop(0)
                cfg, write, read = _perms[0:3]
            else:
                vhost = None
                cfg, write, read = ['', '', '']
            assert ctx.run(rabbitmq.RabbitmqCtl().set_permissions(name, cfg, write, read, vhost=vhost)).ok
        except:
            logger.error('invalid permission specification: "{}"'.format(perms))
            logger.debug(traceback.format_exc())


def exchange(ctx, name, exc_type):
    res = ctx.run(rabbitmq.RabbitmqAdmin().list_exchanges().pipe(file.Grep(r'^|\s' + name + r'\s\+|')))
    exists = res.ok
    print(exists)
    if not exists:
        assert ctx.run(rabbitmq.RabbitmqAdmin().declare_exchange(name, exc_type)).ok


def queue(ctx, name, bindings=None):
    res = ctx.run(rabbitmq.RabbitmqAdmin().list_queues().pipe(file.Grep(r'^|\s' + name + r'\s\+|')))
    exists = res.ok
    print(exists)
    if not exists:
        assert ctx.run(rabbitmq.RabbitmqAdmin().declare_queue(name)).ok
    if isinstance(bindings, (list, tuple)):
        for binding in bindings:
            if not isinstance(binding, (list, tuple)):
                logger.warning('invalid binding "{}": must be list or tuple'.format(binding))
                continue
            try:
                source = binding.pop(0)
            except IndexError:
                logger.warning('empty binding "{}"'.format(binding))
                continue
            try:
                key = binding.pop(0)
            except IndexError:
                key = None
            assert ctx.run(rabbitmq.RabbitmqAdmin().declare_binding(source, name, routing_key=key)).ok


def parameter(ctx, component, name, value):
    res = ctx.run(rabbitmq.RabbitmqAdmin().list_parameters().pipe(file.Grep(r'^|.*|\s' + name + r'\s\+|\s' + component + r'\s+|')))
    exists = res.ok
    print(exists)
    if not exists:
        assert ctx.run(rabbitmq.RabbitmqAdmin().declare_parameter(component, name, value)).ok


def plugins(ctx, plugins: List[str]):
    for plugin in plugins:
        res = ctx.run(rabbitmq.RabbitmqPlugins().list().enabled().pipe(file.Grep(r'{}'.format(plugin))))
        if not res.ok:
            assert ctx.run(rabbitmq.RabbitmqPlugins().enable(plugin)).ok
