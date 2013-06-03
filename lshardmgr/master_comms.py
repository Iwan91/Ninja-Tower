from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import json
from select import select
import time
import struct

def pakf(c):
    s = json.dumps(c)
    return struct.pack('>L', len(s))+s

def read(sck):
    ln = ''
    while len(ln) < 4:
        ln = ln + sck.recv(1)
    datalen = struct.unpack('>L', ln)[0]
    data = ''
    while len(data) < datalen:
        data = data + sck.recv(1)
    return json.loads(data)

def transact(sock, req):
    sock.send(pakf(req))
    return read(sock)


class MasterCommunications(Thread):
    def __init__(self, mc, target_server, idname):
        self.mc = mc
        self.target_addr = target_server
        self.idname = idname
        Thread.__init__(self)

    def __connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(self.target_addr)
        self.socket.settimeout(10)
        self.socket.send(pakf({'request':'first-login', 
                                'id_name':self.mc.id_name,
                                'shards':self.mc.target_shard_number}))

    def run(self):
        while True:
            try:
                self.__connect()
            except Exception as exc:
                print repr(exc)
            else: 
                break

        last_shard_reported = time.time()

        while self.mc.target_shard_number > 0:            
            try:
                rr, ww, xx = select((self.socket, ), (), (), 5)

                if len(rr) == 0:
                    if (time.time() - last_shard_reported) > 30:
                        # should report the shards
                        self.socket.send(pakf({'shards':self.mc.target_shard_number}))
                else:
                    pk = read(self.socket)

                    if pk['request'] == 'allocate-shard':
                        # do we have any shards left?
                        if self.mc.can_allocate_shard():
                            # allocate a shard
                            #
                            #   bpf_chunk is a bpf.txt part with only map_name and players filled in
                            #
                            tcpp, udpp = self.mc.start_new_shard(pk['bpf_chunk'], pk['gugid'])
                            self.socket.send(pakf({'response':'allocated',
                                                   'gugid':pk['gugid'],
                                                   'tcp-interface':self.mc.outside_visible_interface,
                                                   'udp-interface':self.mc.outside_visible_interface,                                                
                                                   'tcp-port':tcpp,
                                                   'udp-port':udpp}))
                        else:
                            self.socket.send(pakf({'response':'recess', 'gugid':pk['gugid']}))
            except Exception as exc:
                print repr(exc)
                try:
                    self.socket.close()
                except:
                    pass
                self.__connect()
                continue

        print 'lshardmgr: Quitting communications'



