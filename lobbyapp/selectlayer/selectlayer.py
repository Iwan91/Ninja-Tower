from Queue import Empty

from satella.channels.sockets import SelectHandlingLayer
from satella.channels import DataNotAvailable, FatalException

from satella.instrumentation.counters import DeltaCounter, PulseCounter
from satella.instrumentation import CounterCollection

from lobbyapp.selectlayer.playersocket import PlayerSocket
from lobbyapp.selectlayer.api import DataArrived, PlayerOnline, PlayerOffline, SendData

class PlayersHandlingLayer(SelectHandlingLayer):
    """
    The layer's tasks is to provide (login, unserialized data)
    or events (login, event instance)
    of data that could interest the upper layer (ie. filter out pings).

    This layer also handles connects and disconnects
    """

    def __init__(self, server_socket, to_eventprocessor, from_eventprocessor, pdbhelper, rootcc):
        """@type server_socket: ServerSocket
        @type to_eventprocessor: L{Queue.Queue}
        @type from_eventprocessor: L{Queue.Queue}
        @param rootcc: root counter collection
        @type rootcc: L{satella.instrumentation.CounterCollection}"""

        SelectHandlingLayer.__init__(self)

        # Set up the server socket and attach it to SL
        self.server_socket = server_socket
        self.register_channel(server_socket)

        # dictionary (user pids => respective PlayerSocket)
        self.authenticated_channels = {}


        # Queue section
        self.to_ep = to_eventprocessor
        self.from_ep = from_eventprocessor

        # PDB section
        self.pdbhelper = pdbhelper

        # Instrumentation section
        cc = CounterCollection('selectlayer')
        self.connections_counter = DeltaCounter('connections', units='connections',
                                                description='SSL connections to server')

        self.outbound_events = PulseCounter('events_to_ep', resolution=60,
                                            units='events per minute',
                                            description='events sent to EventProcessor')
        cc.add(self.connections_counter)
        cc.add(self.outbound_events)
        rootcc.add(cc)

    def on_iteration(self):
        # Check timeouts
        for channel in self.channels:
            if channel != self.server_socket:
                if channel.has_expired():
                    self.close_channel(channel)

        # Process inbound commands
        while True:
            try:
                evt = self.from_ep.get(False)
            except Empty:
                break

            if isinstance(evt, SendData):
                # A request is made to send something to a target socket
                if evt.pid not in self.authenticated_channels:
                    # User not logged in - cannot satisfy
                    continue

                # Else - send it
                self.authenticated_channels[evt.pid].write(evt.data)

    def on_data_frame(self, channel, frame):
        """
        Called by on_readable when there is a frame of data
        from a channel
        """
        # If the user was just authenticated...
        if isinstance(frame, channel.AuthenticatedSuccessfully):
            self.to_ep.put(PlayerOnline(channel.pid))
            self.authenticated_channels[channel.pid] = channel
            self.outbound_events.update()
        else:       # Player is all clear!
            # Relay the data
            self.to_ep.put(DataArrived(channel.pid, frame))
            self.outbound_events.update()

    def on_readable(self, channel):
        if channel == self.server_socket:
            try:
                self.register_channel(PlayerSocket(self.server_socket.read(), self.pdbhelper))
            except DataNotAvailable:
                # Honest to God. Eg. SSL may fail at accept().
                return
            self.connections_counter.update(+1)
        else:
            while True: # process all frames!
                try:
                    data = channel.read()
                except DataNotAvailable:
                    break    # next one, please

                self.on_data_frame(channel, data)
 
    def on_closed(self, channel):
        # If server socket is closed then something is VERY wrong
        assert channel != self.server_socket

        # Signal the counters that we have a connection less
        self.connections_counter.update(-1)

        # If channel was an authenticated channel, we need to inform upstream
        # that the player is no longer logged in

        # note that if we have S1 with given user and S1 connects and presents with
        # the same credentials, S1 channel won't be on authenticated_channels
        # and it's closure won't affect user's logon status

        if channel in self.authenticated_channels.itervalues():
            del self.authenticated_channels[channel.pid]

            self.to_ep.put(PlayerOffline(channel.pid))
            self.outbound_events.update()
