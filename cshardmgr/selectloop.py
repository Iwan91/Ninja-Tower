import struct
import json
from collections import deque
from time import time

from random import choice

from satella.instrumentation import CounterCollection
from satella.instrumentation.counters import DeltaCounter, PulseCounter, \
                                             CallbackCounter
from satella.channels.sockets import Socket, SelectHandlingLayer
from satella.channels import DataNotAvailable, FatalException, \
                             InvalidOperation

from cshardmgr.reqtask import ReqTask

TIME_OUT_SECONDS = 60

class JSONSocket(Socket):
    def __init__(self, socket):
        """@type socket: L{satella.channels.sockets.Socket}"""
        Socket.__init__(self, socket.get_underlying_object())
        self.frames = deque()
        self.last_received_data = time()
        self.who = None

    def has_expired(self):
        """Returns whether the socket has "timed out", ie. there
        was no activity in the time period"""
        return (time() - self.last_received_data) > TIME_OUT_SECONDS

    def read(self, peek=False):
        """
        Attempts to read a JSON frame.

        Throws DataNotAvailable on no data.

        If blocking and null-frame received will return None
        """
        if self.blocking:
            try:
                frame = self.frames.popleft()
                return frame
            except IndexError:
                pass    # we simply need to catch a frame

            # so no cached frames for us. Let's fetch one directly..
            b_fln = Socket.read(self, 4)
            i_fln, = struct.unpack('>L', str(b_fln))

            if i_fln == 0: return None

            pdata = Socket.read(self, i_fln)

            try:
                self.frames.append(json.loads(str(pdata)))
            except ValueError:  # invalid JSON
                self.close()
                raise FatalException, 'Invalid JSON received'                    

            return self.frames.popleft()
        else:
            try:
                frame = self.frames.popleft()
            except IndexError:
                raise DataNotAvailable

            if peek:
                self.frames.appendleft(frame)

            return frame


    def write(self, data):
        """
        Queues a write on the socket.

        @param data: object to JSON-serialize and send
        @type data: JSON-serializable object
        """
        try:
            s_data = json.dumps(data)
        except TypeError:
            # cannot serialize
            raise InvalidOperation, 'Cannot serialize this object'

        Socket.write(self, struct.pack('>L', len(s_data)) + s_data)
            # throws FatalException - let it propagate
            # throws TransientFailure - let it propagate            

    def on_readable(self):
        """Read JSON frames
        Empty frames are None.
        """
        Socket.on_readable(self)

        self.last_received_data = time()

        while True:
            try:
                # peek the frame size (keep in mind we need to remove
                # if from the buffer later, it's only a peek!)
                b_fln = Socket.read(self, 4, peek=True)
                    # this throws DataNotAvailable - we'll catch it later
                    # this throws FatalException - let it propagate

                i_fln, = struct.unpack('>L', str(b_fln))

                if i_fln == 0:
                    # special case - frame size is zero. Consume it
                    # and attempt another frame
                    Socket.read(self, 4)
                    continue

                # Now read the frame (alongside with it's size)
                pdata = Socket.read(self, i_fln+4)
                    # this throws DataNotAvailable - we'll catch it later
                    # this throws FatalException - let it propagate

                try:
                    self.frames.append(json.loads(str(pdata[4:])))
                except ValueError:  # invalid JSON
                    self.close()
                    raise FatalException, 'Invalid JSON received'        
            except DataNotAvailable:
                # all frames readed, good-bye
                break


    # on_readable and on_writable apply, but we
    # can utilize the default ones

class SelectLayer(SelectHandlingLayer):
    """
    Each attached client socket will have a property set.
    sock.who == None        if I don't know this yet
    sock.who == 'l'         lshardmgr
        in that case he has a
            sock.shards == (int)
                with the number of available shards he has
            sock.scheduled = (ReqTask)
                task scheduled right now, or None
    sock.who == 'c'         a client requesting server
        in that case he has a 
            sock.reqtask = (ReqTask)
                task that this client wants us to carry out
    """
    def __init__(self, server_sockets, rootcc):
        SelectHandlingLayer.__init__(self)

        # process server sockets
        self.server_sockets = server_sockets    # there may be many
        for server_socket in server_sockets:
            self.register_channel(server_socket)


        self.reqtasks = []


        # ---------- instrumentation stuff
        self.c_lshardmgrs_connected = DeltaCounter('lshardmgrs_connected', 
                                                   description='Amount of lshardmgrs connected')
        self.c_requests_dispatched = PulseCounter('requests_dispatched', 
                                                  resolution=60, units=u'requests per minute',
                                                  description='Requests to allocate a server sent')
        self.c_alloc_orders = PulseCounter('allocation_orders', resolution=60,
                                           units=u'allocation requests per minute',
                                           description=u'Allocation requests received')
        self.c_requests_success = PulseCounter('requests_successful', resolution=60,
                                               units=u'successful requests per minute',
                                               description=u'Requests successfully executed')
        self.c_requests_failed = PulseCounter('requests_failed', resolution=60,
                                              units=u'failed requests per minute',
                                              description=u'Failed requests')

        def calculate_shards_available():
            a = [x for x in self.channels if x not in self.server_sockets]
            a = [x for x in a if x.who == 'l']
            return sum([x.shards for x in a])

        self.c_shards_available = CallbackCounter('shards_available', calculate_shards_available,
                                                  units=u'shards', description=u'Available shards')
        rootcc.add(self.c_lshardmgrs_connected)
        rootcc.add(self.c_requests_dispatched)
        rootcc.add(self.c_alloc_orders)
        rootcc.add(self.c_requests_success)
        rootcc.add(self.c_requests_failed)
        rootcc.add(self.c_shards_available)

    def on_iteration(self):
        for channel in self.channels:
            if isinstance(channel, JSONSocket):
                if channel.has_expired():
                    self.close_channel(channel)

    def on_readable(self, channel):
        if channel in self.server_sockets:
            try:
                nc = JSONSocket(channel.read())
            except DataNotAvailable:
                pass
            self.register_channel(nc)
        else:

            while True:
                try:
                    elem = channel.read()
                except DataNotAvailable:
                    break

                if channel.who == None:
                    # this packet will ID who this is
                    if 'request' not in elem: return
                    if elem['request'] == 'first-login':
                        # this is a LSHARDMGR

                        try:
                            channel.who = 'l'
                            channel.shards = elem['shards']
                            channel.id_name = elem['id_name']
                            channel.scheduled = None
                        except KeyError:
                            self.close_channel(channel)
                            return

                        # do we have somebody else allocated on this id_name?
                        for chan in self.channels:
                            if chan == channel: continue    # must not be this channel
                            if chan in self.server_sockets: continue    # must not be server socket
                            if chan.who != 'l': continue        # must be lshardmgr

                            if chan.id_name == channel.id_name: 
                                # this is the channel that we should replace
                                self.close_channel(chan)


                        self.c_lshardmgrs_connected.update(+1)
                        self.ac_on_new_lshardmgr_connected(channel)

                    elif elem['request'] == 'allocate-shard':
                        # this is a REQUEST
                        try:
                            channel.who = 'c'
                            channel.reqtask = ReqTask(elem['gugid'], elem['bpf_chunk'])
                            self.reqtasks.append(channel.reqtask)
                        except KeyError:
                            self.close_channel(channel)
                            return

                        self.c_alloc_orders.update()
                        self.ac_on_alloc_request(channel, elem)
                elif channel.who == 'l':
                    if 'shards' in elem:    # ping response
                        if isinstance(elem['shards'], int):
                            channel.chards = elem['shards']

                    if 'response' in elem:
                        # let's see that happened
                        if elem['response'] == 'allocated':
                            # success! allocated
                            self.ac_on_allocation_success(channel, elem)
                            self.c_requests_success.update()
                        elif elem['response'] == 'recess':
                            # failure! not allocate
                            self.ac_on_allocation_recess(channel)
                            self.c_requests_failed.update()

    def on_closed(self, channel):
        if channel in self.server_sockets: return

        if channel.who == 'l':  # lshardmgr channel killed
            self.c_lshardmgrs_connected.update(-1)

            if channel.scheduled != None:   # it it was doing something ...

                self.c_requests_failed.update()

                self.ac_on_lshard_channel_killed(channel)   # .. do the appropriate

    # --------------------------- extra logic for allocation scheduling

    def hlac_alloc(self, reqtask):
        # pick a lshardmgr that has shards
        chans = [x for x in self.channels if x not in self.server_sockets]
        chans = [x for x in chans if x.who == 'l']
        chans = [x for x in chans if x.shards > 0]

        if len(chans) == 0: return False    # simply no shards

        chan = choice(chans)

        chan.scheduled = reqtask
        try:
            chan.write({'request': 'allocate-shard',
                        'bpf_chunk': reqtask.bpf_chunk,
                        'gugid': reqtask.gugid})
        except FatalException:
            # chan failed!
            self.close_channel(chan)

        return True

    def ac_on_lshard_channel_killed(self, channel):
        """
        a lshardmgr channel that was executing something has just been killed
        @param channel: the casualty
        """

        # it's essentially the same as recess..
        self.ac_on_allocation_recess(channel)

    def ac_on_allocation_recess(self, channel):
        """a lshardmgr has failed to allocate a game
        @param channel: lshardmgr channel that executed the query
        @param elem: response that the lshardmgr channel sent"""
        # get the task, unschedule it from channel
        task = channel.scheduled
        channel.scheduled = None

        # first, it's imperative to find the channel that wanted this
        chan = [x for x in self.channels if x not in self.server_sockets]   # no server sockets
        chan = [x for x in chan if x.who == 'c']        # only incoming requests
        chan = [x for x in chan if x.reqtask == task]       # filter the proper channel
        if len(chan) == 0:  # if this is an orphaned request...
            return # then it's fine
        chan, = chan

        try:
            if not task.retry(): raise IOError
            if not self.hlac_alloc(task): raise IOError # attempt to reschedule
        except IOError:
            # this request will not be fulfilled
            chan.reqtask = None
            chan.write({'response': 'recess', 'gugid': task.gugid})

    def ac_on_new_lshardmgr_connected(self, channel):
        """A new lshardmgr has just connected
        @param channel: that lshardmgr's channel"""
        pass # well, good for you!

    def ac_on_allocation_success(self, channel, elem):
        """a lshardmgr has successfully allocated a game
        @param channel: lshardmgr channel that executed the query"""
        # get the task, unschedule it from channel
        task = channel.scheduled
        channel.scheduled = None

        # first, it's imperative to find the channel that wanted this
        chan = [x for x in self.channels if x not in self.server_sockets]   # no server sockets
        chan = [x for x in chan if x.who == 'c']        # only incoming requests
        chan = [x for x in chan if x.reqtask == task]       # filter the proper channel
        if len(chan) == 0:  # if this is an orphaned request...
            return # then it's fine
        chan, = chan

        chan.reqtask = None
        chan.write(elem)

    def ac_on_alloc_request(self, channel, elem):
        """a request to allocate has been received. channel is modified to
        contains a .reqtask field before this is called.
        @param channel: channel that requested it
        @param elem: allocation request message
        @return bool: True if allocation succeeded, False if it didn't
        """
        if not self.hlac_alloc(channel.reqtask):
            # if that happens then there are simply NO SHARDS to allocate
            channel.write({'response': 'recess', 'gugid': elem['gugid']})
            channel.reqtask = None

            self.c_requests_failed.update()