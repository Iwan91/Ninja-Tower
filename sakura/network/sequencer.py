"""Sequencer is a module that represents fused protocolway 
of clients, via using both TCP and UDP to represent them.
This is implemented in receiving server's thread, unfortunately,
so make it short in order to reduce blocking to a necessary minimum"""
from sakura.instrumentation import log
from Queue import Queue
from threading import Lock
from sakura import config
from struct import pack, unpack

class MsgKbdStateUpdate(object):
    def __init__(self, up, right, down, left):
        self.kbd = (up, right, down, left)
class MsgSkillKeyDeployed(object):
    def __init__(self, qkid, x, y, pid):
        self.qkid = qkid
        self.x = x
        self.y = y
        self.target = pid
class MsgPlayerOnline(object): pass
class MsgPlayerOffline(object): pass

class Sequencer(object):
    def __init__(self):
        self.tcp_sockets = {}       # pid: TCP socket
        self.udp_addresses = {}     # pid: UDP address tuple
        self.unverified_sockets = []       # they are yet pending punchthrough verification
        self.rcvd_commands = Queue()
        self.sock_lock = Lock()
        self.udp_socket = config.registry['udp_socket']

    # Commands: to be called by gameworld logic
    def relay_status(self, a, iter):
        """@param a: list of generation-0 UDP parameters
        @param iter: no of current iteration"""
        k = ''.join(['\x00', pack('<L', iter)] + [pack('<BHHHff', *x) for x in a])
        with self.sock_lock:
            for udpaddr in self.udp_addresses.itervalues():
                self.udp_socket.sendto(k, udpaddr)

    def send_score(self, pid, score_t0, score_t1):
        try:
            self.tcp_sockets[pid].socket.direct_send(pack('<BBB', 7, score_t0, score_t1))
        except:
            pass

    def send_game_over(self, who_won):
        with self.sock_lock:
            for tcpsocket in self.tcp_sockets.itervalues():
                tcpsocket.socket.direct_send(pack('<BB', 6, who_won))

    def relay_game_started(self):
        """Game has been started"""
        with self.sock_lock:
            for tcpsocket in self.tcp_sockets.itervalues():
                tcpsocket.socket.direct_send('\x05')

    def relay_game_over(self, team_won):
        with self.sock_lock:
            for tcpsocket in self.tcp_sockets.itervalues():
                tcpsocket.socket.direct_send('\x06'+pack('<B', team_won))

    def relay_repllog(self, strtosend, iter):
        strtosend = ''.join((pack('<L', iter), strtosend))
        # Problem is, this is executed in GameWorld's thread. Thise data must be sent *RIGHT NOW*,
        # we simply can't wait for select loop to do another iteration.
        # Fortunately, we got a right magic incantation to directly send stuff...
        with self.sock_lock:
            for tcpsocket in self.tcp_sockets.itervalues():
                tcpsocket.socket.direct_send('\x04'+strtosend)

    # Events: to be called by select-logic thread
    def on_tcp_player_close(self, pid):
        """Verified TCP socket closed"""
        # send information about player logged out
        with self.sock_lock:
            for sock in self.tcp_sockets.itervalues(): sock.send('\x02'+pack('<H', pid))
            try:
                del self.udp_addresses[pid]
            except:
                print 'Shouldnt happen'
            try:            
                del self.tcp_sockets[pid]
            except:
                print 'May not happen'

        self.rcvd_commands.put((pid, MsgPlayerOffline()))            
    def on_tcp_nonplayer_close(self, socket):
        """Nonverified TCP socket closed"""
        with self.sock_lock:
            self.unverified_sockets.remove(socket)

    def on_tcp_redress(self, pid, newsock):
        """Socket wrapper has just been translated"""
        # nobody uses it, so far

    def on_tcp_packet(self, pid, data):
        try:
            self._on_tcp_packet(pid, data)
        except:
            pass        # data might be arbitrarily malformed
    def _on_tcp_packet(self, pid, data):
        """TCP packet received"""
        if data[0] == 2:        # Chat to All
            with self.sock_lock:
                for sock in self.tcp_sockets.itervalues():
                    sock.send('\x01'+pack('<H', pid)+data[1:])
        elif data[0] == 3:      # Chat to Team
            my_team = config.registry['players']['team']
            for pid, player in config.registry['players']:
                if player['team'] == my_team:
                    try:
                        with self.sock_lock:
                            self.tcp_sockets[pid]
                    except KeyError: # player must be offline
                        pass
                    else:
                        with self.sock_lock:
                            self.tcp_sockets[pid].send('\x00'+pack('<H', pid)+data[1:])
        elif data[0] == 4:      # No operation
            pass
        elif data[0] == 0:      # Keyboard state update
            d = data[1]
            k = MsgKbdStateUpdate(bool(d & 1), bool(d & 4), bool(d & 8), bool(d & 2))            
            self.rcvd_commands.put((pid, k))
        elif data[0] == 1:      # Skill key pressed
            if data[1] > 4: return      # Invalid key pressed.
            x = data[2] + (data[3] << 8)
            y = data[4] + (data[5] << 8) 
            p = data[6] + (data[7] << 8)
            s = MsgSkillKeyDeployed(data[1], x, y, p)
            self.rcvd_commands.put((pid, s))

    def on_udp_packet(self, data, address):
        """On UDP packet received"""
        with self.sock_lock:
            if address in self.udp_addresses.values():      # Logged in user pinging
                packtype = data[0]
                if packtype == '\x00':  # PING request
                    self.udp_socket.sendto('\x01PING', address)
            else:                                           # Unverified (?) user pinging
                for unverified_socket in self.unverified_sockets:
                    if data == unverified_socket.response2: # bingo
                        log('sakura.network.sequencer.Sequencer.on_udp_packet: Verified ', unverified_socket.pid)
                        self.unverified_sockets.remove(unverified_socket)

                        # inform people about player connected
                        for sock in self.tcp_sockets.itervalues(): 
                            sock.send('\x03'+pack('<H', unverified_socket.pid))

                        self.tcp_sockets[unverified_socket.pid] = unverified_socket
                        unverified_socket.on_verified()
                        unverified_socket.send('READY')

                        self.rcvd_commands.put((unverified_socket.pid, MsgPlayerOnline()))
                        self.udp_addresses[unverified_socket.pid] = address
                        return

    def on_register_socket(self, socket):
        """On new socket appears that needs punchthrough validation"""
        with self.sock_lock:
            self.unverified_sockets.append(socket)
            log('sakura.network.sequencer.Sequencer.on_register_socket: Added socket for verification')