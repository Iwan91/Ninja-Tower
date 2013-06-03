from threading import Lock
from struct import pack
from Queue import Queue
from time import time
import struct

class NT1TCPSocket(object):
    def __init__(self, socket):
        self.socket = socket
        self.tx_buffer = bytearray()
        self.rx_buffer = bytearray()
        self.in_packets = []
        self.last_activity = time()

    def has_timed_out(self):
        return time() - self.last_activity > 120        # timeout of 2 minutes

    def wants_to_write(self):
        return len(self.tx_buffer) > 0

    def send(self, data):
        self.tx_buffer.extend(struct.pack('>H', len(data)))
        self.tx_buffer.extend(data)

    def direct_send(self, data):
        dts = struct.pack('>H', len(data)) + data
        try:
            self.socket.send(dts)
        except:
            # Probably timeout.
            # Every reasonably healthy socket has enough buffer space for us to
            # send, except for pathological non-server-like systems.
            # If there is no room in buffer, this means that a very nasty
            # connection spike occurred, or a disconnect.
            # In that case we shall disconnect the client.
            self.socket.close()

    def on_read(self):
        """Throws Exception on socket down"""
        try:
            k = self.socket.recv(512)
        except:
            raise Exception, 'Connection closed abnormally'
        self.last_activity = time()
        if len(k) == 0: raise Exception, 'Connection closed by peer'
        self.rx_buffer.extend(k)

        while len(self.rx_buffer) > 1:      # while there are packets
            dlen = (self.rx_buffer[0] << 8) + self.rx_buffer[1]
            if len(self.rx_buffer) >= (dlen+2):
                self.in_packets.append(self.rx_buffer[2:dlen+2])
                del self.rx_buffer[:dlen+2]
            else:
                break

    def on_write(self):
        try:
            bytes_written = self.socket.send(self.tx_buffer)
        except:
            raise Exception, 'Connection closed abnormally'
        del self.tx_buffer[:bytes_written]

    def close(self):
        try:
            self.socket.close()
        except:
            raise Exception, 'Exception closing a socket (lol wut?)'            

    def fileno(self):
        return self.socket.fileno()
