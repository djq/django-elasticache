from mock import patch, call, MagicMock
from django_elasticache.cluster_utils import (
    get_cluster_info, WrongProtocolData)
from nose.tools import eq_, raises

TEST_PROTOCOL_1 = [
    'VERSION 1.4.14',
    'CONFIG cluster 0 138\r\n1\nhost|ip|port host||port\n\r\nEND\r\n',
]

TEST_PROTOCOL_2 = [
    'VERSION 1.4.13',
    'CONFIG cluster 0 138\r\n1\nhost|ip|port host||port\n\r\nEND\r\n',
]


@patch('django_elasticache.cluster_utils.Telnet')
def test_happy_path(Telnet):
    client = Telnet.return_value
    client.read_until.side_effect = TEST_PROTOCOL_1
    info = get_cluster_info('', 0)
    eq_(info['version'], 1)
    eq_(info['nodes'], ['ip:port', 'host:port'])


@raises(WrongProtocolData)
@patch('django_elasticache.cluster_utils.Telnet', MagicMock())
def test_bad_protocol():
    get_cluster_info('', 0)


@patch('django_elasticache.cluster_utils.Telnet')
def test_last_versions(Telnet):
    client = Telnet.return_value
    client.read_until.side_effect = TEST_PROTOCOL_1
    get_cluster_info('', 0)
    client.write.assert_has_calls([
        call('version\n'),
        call('config get cluster\n'),
    ])


@patch('django_elasticache.cluster_utils.Telnet')
def test_prev_versions(Telnet):
    client = Telnet.return_value
    client.read_until.side_effect = TEST_PROTOCOL_2
    get_cluster_info('', 0)
    client.write.assert_has_calls([
        call('version\n'),
        call('get AmazonElastiCache:cluster\n'),
    ])
