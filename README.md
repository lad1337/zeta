# Zeta

A telegram bot for plex, radarr and later more

## Config

All by environment variables:

```sh
export ZETA_TOKEN=
# allowed chat ids comma separated
export ZETA_ALLOWED=
export ZETA_PLEX_TOKEN=
# with port
export ZETA_PLEX_BASEURL=
export ZETA_RADARR_APIKEY=
# with port
export ZETA_RADARR_BASEURL=
```

## Dev

```
git clone git@github.com:lad1337/zeta.git
cd zeta
mkvirtualenv --python python3 zeta
pip install -e .
# run
zeta-bot
```