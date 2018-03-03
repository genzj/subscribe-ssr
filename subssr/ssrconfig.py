from json import dump
from typing import Any, Dict

REQUIRED_FIELDS = [
    'server',
    'server_port',
    'protocol',
    'method',
    'obfs',
    'password',
]

REQUIRED_FIELDS_POSITION = {
    'server': 0,
    'server_port': 1,
    'protocol': 2,
    'method': 3,
    'obfs': 4,
    'password': 5,
}


EXTRA_FIELDS = [
    'obfsparam',
    'protoparam',
    'remarks',
    'group',
    'udpport',
    'uot',
]


BASE64_FIELDS = [
    'password',
    'obfsparam',
    'protoparam',
    'remarks',
    'group',
]


def save(config: Dict[str, Any], fn=None):
    fn = fn or '{}.json'.format(config.get('remarks', config['server']))
    with open(fn, 'w') as of:
        dump(config, of, indent=4)
    return fn
