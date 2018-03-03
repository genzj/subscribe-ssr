from typing import Optional

import requests


def load(url, proxy: Optional[str]='socks5://127.0.0.1:1080'):
    with requests.session() as session:
        session.proxies = {
            'http': proxy,
            'https': proxy,
        }
        req = session.get(url)
        return req.text
