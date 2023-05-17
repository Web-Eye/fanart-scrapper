import json
import random
import time
import requests


class coverartarchiveAPI:
    def __init__(self):
        self._baseurl = 'http://coverartarchive.org'
        self._requests_session = requests.Session()
        self._request_header = {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                }
        self._minWaittime = 0.5
        self._maxWaittime = 3.5

    def _request(self, _type, mbid):
        url = '/'.join([self._baseurl, _type, mbid])

        conn_tries = 0
        while True:

            try:
                wt = round(random.uniform(self._minWaittime, self._maxWaittime), 2)
                if wt > 0:
                    time.sleep(wt)

                page = self._requests_session.get(url, timeout=3000, headers=self._request_header)
                if page.status_code == 200:
                    return json.loads(page.content)
                else:
                    return None

            except requests.exceptions.ConnectionError as e:
                conn_tries += 1
                if conn_tries > 4:
                    print('exit [max retries are reached]')
                    raise e

                time.sleep(60)

    def getRelease(self, mbid):
        return self._request('release', mbid)

    def getReleaseGroup(self, mbid):
        return self._request('release-group', mbid)