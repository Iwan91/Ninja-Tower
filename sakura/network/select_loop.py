from sakura.instrumentation import log
from select import select
from threading import Thread
from sakura.network.base_packet import NT1TCPSocket
from sakura.network.wrappers import LoggingInWrapper
from sakura import config

class SelectLoop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.tcp_socket = config.registry['tcp_socket']
        self.udp_socket = config.registry['udp_socket']
        self.client_sockets = []        # client TCP socket objects
        self.sequencer = config.registry['_runtime']['sequencer']

    def run(self):
        log('sakura.network.select_loop.SelectLoop: Running network logic')

        config.registry['tcp_socket'].listen(10)

        while True:
            self.loop()

    def loop(self):
        # Get all sockets

        try:
            if config.registry['game_world_processor'] == False:
                print 'sakura.network.select_loop.loop: Terminating'
                raise Exception, 'Terminating'
        except KeyError:
            pass

        r_socks = [self.tcp_socket, self.udp_socket] + self.client_sockets
        w_socks = [x for x in self.client_sockets if x.wants_to_write()]

        try:
            rs, ws, xs = select(r_socks, w_socks, (), 5)
        except:
            for socket in self.client_sockets:
                try:
                    select((socket, ), (), (), 0)
                except:
                    log('sakura.network.select_loop.SelectLoop.loop: Found failed socket in select')
                    self.client_sockets.remove(socket)
                    socket.close()
                    return

        for socket in ws:
            try:
                socket.on_write()
            except:
                log('sakura.network.select_loop.SelectLoop.loop: Failure during on_write')
                self.client_sockets.remove(socket)
                socket.close()
                continue

        for socket in rs:
            if socket == self.tcp_socket:
                log('sakura.network.select_loop.SelectLoop.loop: Accepting a connection')
                sock, addr = socket.accept()
                sock = NT1TCPSocket(sock)
                sock = LoggingInWrapper(sock)
                self.client_sockets.append(sock)
            elif socket == self.udp_socket:
                data, addr = socket.recvfrom(1024)
                self.sequencer.on_udp_packet(data, addr)
            else:
                try:
                    nso = socket.on_read()
                except:
                    log('sakura.network.select_loop.SelectLoop.loop: Failure during on_read')
                    self.client_sockets.remove(socket)
                    socket.close()
                    continue

                if nso != None: # re-wrapping requested
                    self.client_sockets.remove(socket)
                    self.client_sockets.append(nso)

        for socket in self.client_sockets:
            if socket.has_timed_out():
                log('sakura.network.select_loop.SelectLoop.loop: Socket timed out')
                self.client_sockets.remove(socket)
                socket.close()
                return
