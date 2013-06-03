import unittest

from Queue import Queue
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
import ssl
import struct
from time import sleep
from threading import Thread
import json

from satella.channels.sockets import SSLServerSocket, SSLSocket
from satella.threads import BaseThread
from satella.channels import FatalException
from satella.channels.unittests.utils import get_dummy_cert
from satella.instrumentation import CounterCollection

from lobbyapp.selectlayer.api import PlayerOnline, PlayerOffline, PDBHelperInterface, DataArrived, SendData
from lobbyapp.selectlayer.selectlayer import PlayersHandlingLayer

from lobbyapp.selectlayer import jsonsocket # used for monkeypatching timeouts

TESTING_PORT = 50000

class PDBHelperStandin(PDBHelperInterface):
    """Drop-in pseudo-replacement for database interface"""
    def authenticate(self, login, password):
        if login == 'stanislav':
            return 1, 0      # logged in!
        else:
            return -1, None      # invalid credentials

def pkjson(data):
    x = json.dumps(data)
    return struct.pack('>L', len(x))+x

def rdjson(sck):
    ln, = struct.unpack('>L', str(sck.read(4)))
    return json.loads(str(sck.read(ln)))

class BaseLoginTest(unittest.TestCase):

    def setUp(self):
        """Starts the server"""
        self.dummycert_context = get_dummy_cert()
        dncert = self.dummycert_context.__enter__()
        # setup server channel
        servsock = socket(AF_INET, SOCK_STREAM)
        servsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        servsock.bind(('127.0.0.1', TESTING_PORT))
        servsock.listen(10)
        servsock = ssl.wrap_socket(servsock, certfile=dncert)
        servsock = SSLServerSocket(servsock)
        self.servsock = servsock

        jsonsocket.TIME_OUT_SECONDS = 120   # restore sane defaults
            # our test cases monkeypatch it, so there is a need
            # to restore it

        self.events_received, self.events_sent = Queue(), Queue()

        do_nothing_namespace_manager = CounterCollection('test')

        phl = PlayersHandlingLayer(servsock, 
                                   self.events_received,
                                   self.events_sent,
                                   PDBHelperStandin(),
                                   do_nothing_namespace_manager)

        class PHLingThread(BaseThread):
            def __init__(self, phl):
                BaseThread.__init__(self)
                self.phl = phl

            def run(self):
                while not self._terminating:
                    self.phl.select()

        self.phlt = PHLingThread(phl)
        self.phlt.start()

    def tearDown(self):
        """Closes the server"""
        self.phlt.terminate()
        self.phlt.join()
        self.servsock.settimeout(None)  # so that closing is synchronous
        self.servsock.close()
        self.dummycert_context.__exit__(None, None, None)


        # ---------------- TEST CASES

    def test_successful_connect(self):
        """
        Tests logging in on valid credentials
        """
        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        sock.connect(('127.0.0.1', TESTING_PORT))
        sock = SSLSocket(sock)

        sock.settimeout(5)

        sock.write(pkjson({'login': 'stanislav', 'password': 'bear'}))
        response = rdjson(sock)

        self.assertEquals(response['status'], 'ok')
        self.assertEquals(isinstance(self.events_received.get(), PlayerOnline), True)

    def test_failed_connect(self):
        """
        Tests logging in on invalid credentials
        """
        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        sock.connect(('127.0.0.1', TESTING_PORT))
        sock = SSLSocket(sock)

        sock.settimeout(5)

        sock.write(pkjson({'login': 'stanislavv', 'password': 'bear'}))
        response = rdjson(sock)

        self.assertEquals(response['status'], 'fail')

    def test_timeout(self):
        """
        Tests sock failing due to timeout
        """
        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        sock.connect(('127.0.0.1', TESTING_PORT))
        sock = SSLSocket(sock)

        jsonsocket.TIME_OUT_SECONDS = 5

        sock.settimeout(15)

        self.assertRaises(FatalException, sock.read, 1)

    def test_login_and_timeout(self):
        """
        Tests logging in and then timeouting
        """
        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        sock.connect(('127.0.0.1', TESTING_PORT))
        sock = SSLSocket(sock)

        sock.settimeout(15)
        jsonsocket.TIME_OUT_SECONDS = 5

        sock.write(pkjson({'login': 'stanislav', 'password': 'bear'}))
        response = rdjson(sock)
        self.assertEquals(isinstance(self.events_received.get(), PlayerOnline), True)

        self.assertRaises(FatalException, sock.read, 1)       # timeout

        # we should be signalled as timeouters
        self.assertEquals(isinstance(self.events_received.get(), PlayerOffline), True)

    def test_patchthru_connect(self):
        """
        Tests relaying data from EventProcessor to SelectLayer
        """        
        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        sock.connect(('127.0.0.1', TESTING_PORT))
        sock = SSLSocket(sock)

        sock.settimeout(7)

        sock.write(pkjson({'login': 'stanislav', 'password': 'bear'}))
        response = rdjson(sock)

        self.assertEquals(response['status'], 'ok')

        # at this point stanislav is logged in and we can force sending data
        self.events_sent.put(SendData(1, {'hello': 'world'}))

        jsp = rdjson(sock)
        self.assertEquals(jsp['hello'], 'world')

    def test_patchinfo_connect(self):
        """
        Tests relaying data from SelectLayer to EventProcessor
        """
        sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM))
        sock.connect(('127.0.0.1', TESTING_PORT))
        sock = SSLSocket(sock)

        sock.settimeout(5)

        sock.write(pkjson({'login': 'stanislav', 'password': 'bear'}))
        response = rdjson(sock)

        self.assertEquals(response['status'], 'ok')
        self.assertEquals(isinstance(self.events_received.get(), PlayerOnline), True)

        sock.write(pkjson({'test_data': 'indeed'}))
        el = self.events_received.get()

        self.assertEquals(isinstance(el, DataArrived), True)
        self.assertEquals(el.pid, 1)
        self.assertEquals(el.data['test_data'], 'indeed')

