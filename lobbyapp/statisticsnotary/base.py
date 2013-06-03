from satella.channels.sockets import SelectHandlingLayer, Socket
from satella.channels import DataNotAvailable

from lobbyapp.selectlayer.jsonsocket import JSONSocket

from lobbyapp.playerdb.transactions import TRRoundEnded

class StatisticsNotary(SelectHandlingLayer):
    def __init__(self, pdb, socket):
        SelectHandlingLayer.__init__(self)
        self.server_socket = socket
        self.pdb = pdb

        self.register_channel(self.server_socket)

    def on_iteration(self):
        for channel in [x for x in self.channels if x != self.server_socket]:
            if channel.has_expired():
                self.close_channel(channel)

    def on_readable(self, channel):
        # sanity checks - packet present and valid
        if channel == self.server_socket:
            try:
                self.register_channel(JSONSocket(self.server_socket.read()))                
            except DataNotAvailable:
                pass
        else:
            try:
                chand = channel.read()
            except DataNotAvailable:
                return

            print 'LA: Received %s' % chand

            if 'gugid' not in chand: return
            if 'winner' not in chand: return
            if 'status' not in chand: return

            TRRoundEnded(self.pdb, chand['gugid'], chand).start()