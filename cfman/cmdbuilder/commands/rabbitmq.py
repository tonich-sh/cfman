
import json

from typing import ForwardRef

from ..cmd import Cmd, LongOpt, Opt, Subcommand


__all__ = ['RabbitmqCtl', 'RabbitmqAdmin']


class ListUsers(Subcommand):
    def __init__(self, ctl):
        super(ListUsers, self).__init__('list_users', ctl)


class ChangePassword(Subcommand):
    __slots__ = ['_user_name', '_password']

    def __init__(self, ctl, user_name, password):
        super(ChangePassword, self).__init__('change_password', ctl)
        self._user_name = user_name
        self._password = password

    @property
    def opts(self):
        return self._opts + [self._user_name, self._password]


class AddUser(Subcommand):
    __slots__ = ['_user_name', '_password']

    def __init__(self, ctl, user_name, password):
        super(AddUser, self).__init__('add_user', ctl)
        self._user_name = user_name
        self._password = password

    @property
    def opts(self):
        return self._opts + [self._user_name, self._password]


class SetUserTags(Subcommand):
    __slots__ = ['_user_name', '_tags']

    def __init__(self, ctl, user_name, tags):
        super(SetUserTags, self).__init__('set_user_tags', ctl)
        self._user_name = user_name
        self._tags = tags

    @property
    def opts(self):
        return [self._user_name] + self._tags


class SetPermissions(Subcommand):
    __slots__ = ['_user_name', '_perms', '_vhost']

    def __init__(self, ctl, user_name, perms, vhost=None):
        super(SetPermissions, self).__init__('set_permissions', ctl)
        self._user_name = user_name
        self._perms = perms
        self._vhost = vhost

    @property
    def opts(self):
        if self._vhost is not None:
            v = ['-p', self._vhost]
        else:
            v = []
        return v + [self._user_name] + self._perms


class RabbitmqCtl(Cmd):

    def __init__(self):
        super(RabbitmqCtl, self).__init__('rabbitmqctl')

    def add_user(self, user_name, password):
        """add_user <username> <password>"""
        return AddUser(self, user_name, password)

    # TODO: delete_user <username>

    def change_password(self, user_name, password):
        """change_password <username> <newpassword>"""
        return ChangePassword(self, user_name, password)

    # TODO: clear_password <username>
    # TODO: authenticate_user <username> <password>

    def set_user_tags(self, user_name, tags):
        """set_user_tags <username> <tag> ..."""
        return SetUserTags(self, user_name, tags)

    def list_users(self):
        """list_users"""
        return ListUsers(self)

    # add_vhost <vhost>
    # delete_vhost <vhost>
    # list_vhosts [<vhostinfoitem> ...]

    def set_permissions(self, user_name, conf, write, read, vhost=None):
        """set_permissions [-p <vhost>] <user> <conf> <write> <read>"""
        return SetPermissions(self, user_name, [conf, write, read], vhost=vhost)

    # clear_permissions [-p <vhost>] <username>
    # list_permissions [-p <vhost>]
    # list_user_permissions <username>

    def list_exchanges(self):
        """list_exchanges [-p <vhost>] [<exchangeinfoitem> ...]"""
        return ListExchanges(self)


class AdminList(Subcommand):
    __slots__ = ['_subopt']

    def __init__(self, ctl):
        super(AdminList, self).__init__('list', ctl)
        self._opts.append(self._subopt)


class ListExchanges(AdminList):
    __slots__ = []
    _subopt = 'exchanges'


class ListBindings(AdminList):
    __slots__ = []
    _subopt = 'bindings'


class ListQueues(AdminList):
    __slots__ = []
    _subopt = 'queues'


class ListParameters(AdminList):
    __slots__ = []
    _subopt = 'parameters'


class DeclareExchange(Subcommand):
    __slots__ = ['_name', '_type']

    def __init__(self, ctl, name, exc_type):
        super(DeclareExchange, self).__init__('declare', ctl)
        self._opts.append('exchange')
        self._name = LongOpt('name', name)
        self._type = LongOpt('type', exc_type)

    @property
    def opts(self):
        return self._opts + [self._name, self._type]


class DeclareQueue(Subcommand):
    __slots__ = ['_name']

    def __init__(self, ctl, name):
        super(DeclareQueue, self).__init__('declare', ctl)
        self._opts.append('queue')
        self._name = LongOpt('name', name)

    @property
    def opts(self):
        return self._opts + [self._name]


class DeclareBinding(Subcommand):
    __slots__ = ['_source', '_destination', '_routing_key']

    def __init__(self, ctl, source, destination, routing_key=None):
        super(DeclareBinding, self).__init__('declare', ctl)
        self._opts.append('binding')
        self._source = LongOpt('source', source)
        self._destination = LongOpt('destination', destination)
        self._routing_key = LongOpt('routing_key', routing_key) if routing_key is not None else None

    @property
    def opts(self):
        ret = self._opts + [self._source, self._destination]
        if self._routing_key is not None:
            ret.append(self._routing_key)
        return ret


class DeclareParameter(Subcommand):
    __slots__ = ['_component', '_name', '_value']

    def __init__(self, ctl, component, name, value):
        super(DeclareParameter, self).__init__('declare', ctl)
        self._opts.append('parameter')
        self._component = LongOpt('component', component)
        self._name = LongOpt('name', name)
        self._value = value

    @property
    def opts(self):
        ret = self._opts + [self._component, self._name]
        if isinstance(self._value, dict):
            value = json.dumps(self._value)
        else:
            value = self._value
        ret.append(LongOpt('value', value))
        return ret


class DeleteParameter(Subcommand):
    __slots__ = ['_component', '_name']

    def __init__(self, ctl, component, name):
        super(DeleteParameter).__init__('delete', ctl)
        self._opts.append('parameter')
        self._component = LongOpt('component', component)
        self._name = LongOpt('name', name)

    @property
    def opts(self):
        ret = self._opts + [self._component, self._name]
        return ret


class RabbitmqAdmin(Cmd):

    def __init__(self):
        super(RabbitmqAdmin, self).__init__('rabbitmqadmin')

    def list_exchanges(self):
        return ListExchanges(self)

    def declare_exchange(self, name, exc_type, ):
        """declare exchange name=... type=... [auto_delete=... internal=... durable=... arguments=...]"""
        return DeclareExchange(self, name, exc_type)

    def list_queues(self):
        """list queues"""
        return ListQueues(self)

    def declare_queue(self, name):
        """declare queue name=... [node=... auto_delete=... durable=... arguments=...]"""
        return DeclareQueue(self, name)

    def list_bindings(self):
        """list bindings"""
        return ListBindings(self)

    def declare_binding(self, source, destination, routing_key=None):
        """declare binding source=... destination=... [arguments=... routing_key=... destination_type=...]"""
        return DeclareBinding(self, source, destination, routing_key=routing_key)

    def list_parameters(self):
        """list paramters [<column>...]"""
        return ListParameters(self)

    def declare_parameter(self, component, name, value):
        """declare parameter component=... name=... value=..."""
        return DeclareParameter(self, component, name, value)

    def delete_parameter(self, component, name):
        return DeleteParameter(self, component, name)


class ListPlugins(Subcommand):
    __slots__ = []

    def __init__(self, parent: ForwardRef('RabbitmqPlugins')):
        super(ListPlugins, self).__init__('list', parent)

    def enabled(self):
        self._opts.append('--enabled')
        return self


class EnablePlugin(Subcommand):
    __slots__ = ['_plugins']

    def __init__(self, parent: ForwardRef('RabbitmqPlugins'), plugin: str = ''):
        super(EnablePlugin, self).__init__('enable', parent)
        if plugin:
            self._plugins = {plugin, }
        else:
            self._plugins = set()

    def plugin(self, plugin):
        self._plugins.add(plugin)
        return self

    @property
    def opts(self):
        return list(self._plugins)


class RabbitmqPlugins(Cmd):

    def __init__(self):
        super(RabbitmqPlugins, self).__init__('rabbitmq-plugins')

    def list(self):
        """list[-v][-m][-E][-e][ < pattern >]"""
        return ListPlugins(self)

    def enable(self, plugin):
        """enable [--offline] [--online] <plugin> ..."""
        return EnablePlugin(self, plugin)

    def disable(self):
        """disable [--offline] [--online] <plugin> ..."""
        raise NotImplementedError

    def set(self):
        """set [--offline] [--online] <plugin> ..."""
        raise NotImplementedError
