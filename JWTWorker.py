import threading
import pyglet
import requests

DEFAULT_JWT_EXPIRATION_TIME = 10 * 60  # 10 minutes


class JWTWorker:
    def __init__(self, credentials: dict, auth_url: str, refresh_url: str, refresh_time: int):
        # PRIVATE
        self.__auth_endpoint = auth_url
        self.__refresh_endpoint = refresh_url
        # PUBLIC
        self.api_token = None
        self.credentials = credentials
        self.refresh_time = DEFAULT_JWT_EXPIRATION_TIME
        # Callbacks
        self.on_auth = lambda: None
        self.on_refresh = lambda: None
        self.on_auth_failed = lambda: None
        self.on_refresh_failed = lambda: None

    def auth(self, __=None):
        """ Get new token from the server """
        r = requests.post(self.__auth_endpoint, data=self.credentials)
        if r.status_code != 200:
            self.on_auth_failed()
            pass
        try:
            r_obj = r.json()
            self.api_token = r_obj['token']
            self.on_auth()
        except KeyError:
            self.on_auth_failed()
            # TODO: SHOW ERROR

    def refresh_token(self, __=None):
        """ Get refresh token from the server using existent token """
        if self.api_token is None:
            self.auth()
            return
        headers = {"Authorization": "Bearer " + self.api_token}
        r = requests.post(self.__refresh_endpoint, headers=headers)
        if r.status_code == 200:
            r_obj = r.json()
            if 'token' in r_obj:
                self.api_token = r_obj['token']
                self.on_refresh()
                return
        # TODO: SHOW ERROR
        self.on_refresh_failed()

    def run(self):
        self.auth()
        pyglet.clock.schedule_interval(self.refresh_token, self.refresh_time)
        t = threading.Thread(target=lambda: pyglet.app.run())
        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start() 
