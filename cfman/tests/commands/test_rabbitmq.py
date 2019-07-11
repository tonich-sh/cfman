from cfman.cmdbuilder.commands import rabbitmq
from cfman.cmdbuilder.compiler import compiler


def test_rabbitmqctl_list_users():
    cmd = rabbitmq.RabbitmqCtl().list_users()
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqctl list_users'


def test_rabbitmqctl_change_password():
    cmd = rabbitmq.RabbitmqCtl().change_password('test', 'test')
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqctl change_password test test'


def test_rabbitmqctl_add_user():
    cmd = rabbitmq.RabbitmqCtl().add_user('test', 'test')
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqctl add_user test test'


def test_rabbitmqadmin_list():
    cmd = rabbitmq.RabbitmqAdmin().list_exchanges()
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqadmin list exchanges'

    cmd = rabbitmq.RabbitmqAdmin().list_queues()
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqadmin list queues'

    cmd = rabbitmq.RabbitmqAdmin().list_bindings()
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqadmin list bindings'


def test_rabbitmqadmin_declare_exchange():
    cmd = rabbitmq.RabbitmqAdmin().declare_exchange('test', 'fanout')
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqadmin declare exchange name=test type=fanout'


def test_rabbitmqadmin_declare_binding():
    cmd = rabbitmq.RabbitmqAdmin().declare_binding('src', 'dst', routing_key='key')
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqadmin declare binding source=src destination=dst routing_key=key'

    cmd = rabbitmq.RabbitmqAdmin().declare_binding('src', 'dst')
    s, params = compiler(cmd, None)
    assert s == 'rabbitmqadmin declare binding source=src destination=dst'
