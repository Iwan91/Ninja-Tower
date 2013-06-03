import struct
import json
from collections import deque
from time import time

from satella.channels.sockets import Socket
from satella.channels import DataNotAvailable, FatalException, \
                             InvalidOperation

TIME_OUT_SECONDS = 120

class JSONSocket(Socket):
    def __init__(self, socket):
        """@type socket: L{satella.channels.sockets.Socket}"""
        Socket.__init__(self, socket.get_underlying_object())
        self.frames = deque()
        self.last_received_data = time()

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
                pass    # we simply need to catch a new frame

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
