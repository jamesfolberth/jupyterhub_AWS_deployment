# Taken from
#https://github.com/yuvipanda/jupyterhub-dummy-authenticator/blob/master/dummyauthenticator/dummyauthenticator.py
from jupyterhub.auth import Authenticator

from tornado import gen

class DummyAuthenticator(Authenticator):
    @gen.coroutine
    def authenticate(self, handler, data):
        return data['username']
