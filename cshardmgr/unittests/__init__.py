import unittest

from time import sleep
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, socket

from cshardmgr.selectloop import SelectLayer, JSONSocket
from satella.threads import BaseThread
from satella.instrumentation import CounterCollection
from satella.channels.sockets import Socket, ServerSocket
from satella.channels import DataNotAvailable, ChannelClosed

TESTING_PORT = 8000

class CshardmgrTests(unittest.TestCase):

    def setUp(self):
        # initialize cshardmgr test socket
        ss = socket(AF_INET, SOCK_STREAM)
        ss.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        ss.bind(('127.0.0.1', TESTING_PORT))
        ss.listen(10)

        ss = ServerSocket(ss)
        sl = SelectLayer([ss], CounterCollection('dontcare'))

        class SelectLayerThread(BaseThread):
            def __init__(self, sl):
                BaseThread.__init__(self)
                self.sl = sl

            def run(self):
                while not self._terminating:
                    self.sl.select()

                for channel in self.sl.channels:
                    self.sl.close_channel(channel)

        self.slt = SelectLayerThread(sl).start()

    def tearDown(self):
        self.slt.terminate().join()

    def test_no_lshardmgrs_single_request(self):
        """Tests how to server fails if there's a request and NO lshardmgrs connected"""

        s = socket(AF_INET, SOCK_STREAM)
        s.connect(('127.0.0.1', TESTING_PORT))
        s = JSONSocket(Socket(s))

        s.write({'request': 'allocate-shard',
                 'gugid': 'trololo',
                 'bpf_chunk': {
                    'map_name': 'Indianapolis',
                    'players': []
                 }})

        rsp = s.read()
        self.assertEquals(rsp['response'], 'recess')
        self.assertEquals(rsp['gugid'], 'trololo')


    class LShardmgr(BaseThread):
        def __init__(self, idname, fail=False):
            """@param fail: whether to fail allocations"""
            BaseThread.__init__(self)
            self.fail = fail
            self.idname = idname

        def run(self):
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(('127.0.0.1', TESTING_PORT))
            s = JSONSocket(Socket(s))
            s.write(({'request': 'first-login',
                      'id_name': self.idname,
                      'shards': 1}))
            s.settimeout(20)

            while not self._terminating:
                try:
                    rd = s.read()
                except DataNotAvailable:
                    s.write({'shards': 1})
                    continue
                except ChannelClosed:
                    return

                # allocation request readed
                if self.fail:
                    s.write({'response': 'recess', 'gugid': rd['gugid']})
                else:
                    s.write({'response': 'allocated',
                             'gugid': rd['gugid'],
                             'tcp-interface': 'a', 'udp-interface': 'b',
                             'tcp-port': 10, 'udp-port': 20})

    def test_single_lshardmgrs_single_request(self):
        """Tests how to server allocates if there's a request and admittant lshardmgr connected"""
        self.LShardmgr('admit', fail=False).start()
        sleep(0.01)

        s = socket(AF_INET, SOCK_STREAM)
        s.connect(('127.0.0.1', TESTING_PORT))
        s = JSONSocket(Socket(s))

        s.write({'request': 'allocate-shard',
                 'gugid': 'trololo',
                 'bpf_chunk': {
                    'map_name': 'Indianapolis',
                    'players': []
                 }})

        rsp = s.read()
        self.assertEquals(rsp['response'], 'allocated')
        self.assertEquals(rsp['gugid'], 'trololo')        

    def test_two_lshardmgrs_single_request(self):
        """Tests how to server allocates if there's a request and admittant lshardmgr connected,
        and a failing lshardmgr connected.

        This test is not deterministic, if it fails try again.
        """
        self.LShardmgr('admit', fail=False).start()
        self.LShardmgr('faily', fail=True).start()
        sleep(0.01)


        for x in xrange(0, 20):
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(('127.0.0.1', TESTING_PORT))
            s = JSONSocket(Socket(s))

            s.write({'request': 'allocate-shard',
                     'gugid': 'trololo',
                     'bpf_chunk': {
                        'map_name': 'Indianapolis',
                        'players': []
                     }})

            rsp = s.read()
            self.assertEquals(rsp['response'], 'allocated')
            self.assertEquals(rsp['gugid'], 'trololo')    

            s.close()    
