from sakura.instrumentation import log 
from sakura import config
from hashlib import sha1

class SequencerRegistered(object):
    def __init__(self, socket, pid, login, challenge2, response2):
        self.socket = socket
        self.pid = pid
        self.login = login
        self.challenge2 = challenge2
        self.response2 = response2
        self.sequencer = config.registry['_runtime']['sequencer']
        self.sequencer.on_register_socket(self)
        self.verified = False

    def on_verified(self):
        self.verified = True

    def on_read(self):
        self.socket.on_read()
        for pak in self.socket.in_packets:
            self.sequencer.on_tcp_packet(self.pid, pak)
        self.socket.in_packets = []

    def has_timed_out(self): return self.socket.has_timed_out()
    def on_write(self): return self.socket.on_write()
    def wants_to_write(self): return self.socket.wants_to_write()
    def send(self, s): return self.socket.send(s)
    def fileno(self): return self.socket.fileno()
    def close(self):
        if self.verified:
            self.sequencer.on_tcp_player_close(self.pid)
        else:
            self.sequencer.on_tcp_nonplayer_close(self)
        self.socket.close()    


STATE_AWAITING_LOGIN = 1
STATE_AWAITING_RESPONSE_1 = 2

class LoggingInWrapper(object):
    def __init__(self, socket):
        self.socket = socket
        self.state = STATE_AWAITING_LOGIN

    def on_write(self): return self.socket.on_write()
    def on_read(self):
        self.socket.on_read()
        log('sakura.network.wrappers.LoggingInWrapper.on_read: starting')

        if len(self.socket.in_packets) > 0:
            inbound = self.socket.in_packets.pop(0)
            if self.state == STATE_AWAITING_LOGIN:
                login = str(inbound).lower()
                try:
                    for pid, player in config.registry['players'].iteritems():
                        if player['login'].lower() == login:
                            self.player_profile = player
                    self.player_profile     # throws Exception
                except KeyError:
                    log('sakura.network.wrappers.LoggingInWrapper.on_read: No such player as requested')
                    self.close()
                    return

                # Generate challenge and response, send it
                self.challenge1 = 'alwaysthesun'
                self.response1 = sha1(self.player_profile['password'] + self.challenge1).hexdigest()
                self.send(self.challenge1)
                self.state = STATE_AWAITING_RESPONSE_1
            elif self.state == STATE_AWAITING_RESPONSE_1:
                if self.response1 != str(inbound):
                    log('sakura.network.wrappers.LoggingInWrapper.on_read: Invalid response1')
                    self.close()
                    return

                challenge2 = 'somemoresun'
                response2 = sha1(self.player_profile['password'] + challenge2).hexdigest()

                self.send(config.registry['map_name'].encode('utf8') + '\xFF' + challenge2)

                # Prepare player info for sending
                pinfotab = []
                for pid, player_profile in config.registry['players'].iteritems():
                    pinfotab.append(str(player_profile['pid']))
                    pinfotab.append(str(player_profile['login']))
                    pinfotab.append(str(player_profile['team']))
                    pinfotab.append(str(player_profile['character']['name']))

                self.send('\xFF'.join(pinfotab))

                return SequencerRegistered(self.socket, self.player_profile['pid'],
                                           self.player_profile['login'], challenge2, response2)

    def wants_to_write(self): return self.socket.wants_to_write()
    def has_timed_out(self): return self.socket.has_timed_out()
    def send(self, s):
        return self.socket.send(s)
    def fileno(self): return self.socket.fileno()
    def close(self): return self.socket.close()