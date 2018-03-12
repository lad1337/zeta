import os
from collections import namedtuple

APP_NAME = 'ZETA'

_NOT_SET = "NOT-SET"

DEFAULT = {
    'token': (str, _NOT_SET),
    'allowed': (lambda x: set(map(int, x.split(','))), ''),
    'admins': (lambda x: set(map(int, x.split(','))), ''),
    'plex_token': (str, _NOT_SET),
    'plex_baseurl': (str, _NOT_SET),
    'radarr_apikey': (str, _NOT_SET),
    'radarr_baseurl': (str, _NOT_SET),
    'template_dir': (str, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'messages'))
}


S = namedtuple('Settings', list(DEFAULT))


settings = S(**{
    k: DEFAULT[k][0](os.environ.get(f'{APP_NAME}_{k}'.upper(), DEFAULT[k][1]))
    for k, v in DEFAULT.items()
})
