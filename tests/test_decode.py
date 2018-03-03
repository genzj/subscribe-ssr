import base64
import json
import tempfile

import os
import requests_mock

from subssr import decode, ssrconfig

data = r'ssr://MTI3LjAuMS4yOjg5NjQ6YXV0aF9hZXMxMjhfc2hhMTpjaGFjaGEyMC1pZXR' +\
       'mOmh0dHBfc2ltcGxlOldGaFlNVEl6Tkhwby8_b2Jmc3BhcmFtPTVyZTM1cmVHNVktQ' +\
       'zVwV3cmcHJvdG9wYXJhbT01cldMNkstVjU3dVQ1cDZjJnJlbWFya3M9Wm05eUxYUmx' +\
       'jM1F0NXJXTDZLLVY1NVNvJmdyb3VwPWRHVnpkRWR5YjNWdw'

ss_data = r'ss://YmYtY2ZiOnRlc3RAMTkyLjE2OC4xMDAuMTo4ODg4Cg'
invalid_data = 'abcdefg'


def test_ssr_base64_decode():
    decoded = decode.ssr_base64_decode(data)
    assert decoded == '127.0.1.2:8964:auth_aes128_sha1:' +\
                      'chacha20-ietf:http_simp' +\
                      'le:WFhYMTIzNHpo/?obfsparam=' +\
                      '5re35reG5Y-C5pWw&protoparam=5rWL6K-' +\
                      'V57uT5p6c&remarks=Zm9yLXRlc3Qt5rWL6K-' +\
                      'V55So&group=dGVzdEdyb3Vw'


def test_ssr_url_parse():
    url = decode.ssr_url_parse(data)
    assert url.scheme == 'ssr'
    assert url.netloc == '127.0.1.2:8964:auth_aes128_sha1:' + \
                         'chacha20-ietf:http_s' + \
                         'imple:WFhYMTIzNHpo'
    assert url.query == 'obfsparam=5re35reG5Y-C5pWw&protoparam=5rWL6K-' +\
                        'V57uT5p6c&remarks=Zm9yLXRlc3Qt5rWL6K-V55So&gr' +\
                        'oup=dGVzdEdyb3Vw'


def test_ssr_required_field_getter():
    rf = decode.ssr_required_field_getter(data)
    assert rf('server') == '127.0.1.2'
    assert rf('server_port') == '8964'
    assert rf('protocol') == 'auth_aes128_sha1'
    assert rf('method') == 'chacha20-ietf'
    assert rf('obfs') == 'http_simple'
    assert rf('password') == 'XXX1234zh'


def test_ssr_extra_param_getter():
    pg = decode.ssr_extra_param_getter(data)
    assert pg('obfsparam') == u'混淆参数'
    assert pg('protoparam') == u'测试结果'
    assert pg('remarks') == u'for-test-测试用'
    assert pg('group') == u'testGroup'
    assert pg('udpport') is None
    assert pg('uot') is None
    assert pg('not-exist') is None


def test_ssr_required_fields():
    fields = decode.ssr_required_fields(data)
    assert fields == {
        'server': '127.0.1.2',
        'server_port': '8964',
        'protocol': 'auth_aes128_sha1',
        'method': 'chacha20-ietf',
        'obfs': 'http_simple',
        'password': 'XXX1234zh',
    }


def test_ssr_extra_params():
    params = decode.ssr_extra_params(data)
    assert params == {
        'obfsparam': u'混淆参数',
        'protoparam': u'测试结果',
        'remarks': u'for-test-测试用',
        'group': u'testGroup',
    }


def test_ssr_config():
    config = decode.ssr_config(data)
    assert config == {
        'server': '127.0.1.2',
        'server_port': '8964',
        'protocol': 'auth_aes128_sha1',
        'method': 'chacha20-ietf',
        'obfs': 'http_simple',
        'password': 'XXX1234zh',
        'obfsparam': u'混淆参数',
        'protoparam': u'测试结果',
        'remarks': u'for-test-测试用',
        'group': u'testGroup',
    }


def test_ssr_config_from_url():
    with requests_mock.Mocker() as m:
        url = 'mock://test.host/ssrconfig'
        text = '\n'.join([
            ss_data, data, invalid_data,
        ])
        text = base64.urlsafe_b64encode(
            text.encode('utf-8')
        ).decode('ASCII')
        m.get(
            url,
            text=text
        )
        configs = list(
            decode.ssr_config_from_url(url)
        )
    assert configs == [{
        'server': '127.0.1.2',
        'server_port': '8964',
        'protocol': 'auth_aes128_sha1',
        'method': 'chacha20-ietf',
        'obfs': 'http_simple',
        'password': 'XXX1234zh',
        'obfsparam': u'混淆参数',
        'protoparam': u'测试结果',
        'remarks': u'for-test-测试用',
        'group': u'testGroup',
    }]


def test_save():
    pwd = os.getcwd()
    try:
        tempdir = tempfile.mkdtemp('-test')
        os.chdir(tempdir)
        config = decode.ssr_config(data)

        fn = ssrconfig.save(config)

        assert os.path.isfile(fn)

        with open(fn, 'rb') as inf:
            config_read = json.load(inf)
        assert config == config_read
        os.remove(fn)
        os.chdir(pwd)
        os.removedirs(tempdir)
    finally:
        os.chdir(pwd)
