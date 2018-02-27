import logging

import requests
from requests import request

logger = logging.getLogger(__name__)

class Client:

    def __init__(self, baseurl, apikey):
        self.baseurl = baseurl.rstrip('/')
        self.headers ={
            'X-Api-Key': apikey
        }

    def request(self, method, path, params=None, json=None):
        resp = requests.request(
            method, f"{self.baseurl}{path}", params=params, json=json, headers=self.headers)
        logger.debug(f"{resp.request.method} {resp.url} {resp.status_code}")
        return resp

    def search(self, term):
        return self.request('GET', "/movie/lookup", params={'term': term}).json()

    def add_movie(self, movie):
        payload = {
            "title": movie['title'],
            "year": movie['year'],
            "qualityProfileId": 6, # 6 = 1080 p / 720 p
            "titleSlug": movie['titleSlug'],
            "tmdbId": movie['tmdbId'],
            "images": movie['images'],
            "rootFolderPath": '/movies/',
            "monitored": True,
            "minimumAvailability": 'preDB',
            "addOptions": {
                "searchForMovie": True
            }
        }
        return self.request('POST', "/movie", json=payload)
