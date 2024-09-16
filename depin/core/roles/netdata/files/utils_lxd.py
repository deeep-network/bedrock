#!/usr/bin/env python3
import requests
import socket

from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from requests.adapters import HTTPAdapter

class LXDConnection(HTTPConnection):
    def __init__(self):
        super().__init__("localhost")

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect("/dev/lxd/sock")

class LXDConnectionPool(HTTPConnectionPool):
    def __init__(self):
        super().__init__("localhost")

    def _new_conn(self):
        return LXDConnection()

class LXDAdapter(HTTPAdapter):
    def get_connection_with_tls_context(self, request, verify, proxies=None, cert=None):
        return LXDConnectionPool()

def lxd_get(endpoint):
    try:
      lxd = requests.Session()
      lxd.mount("http://lxd/", LXDAdapter())
      response = lxd.get(f"http://lxd/{endpoint}")
      if isinstance (response, str):
          response = {'value': response}
    except:
      response = {'value': 'unknown'}
    return response
