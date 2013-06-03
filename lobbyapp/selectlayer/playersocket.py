from satella.channels import DataNotAvailable

from lobbyapp.selectlayer.jsonsocket import JSONSocket

class PlayerSocket(JSONSocket):

    class AuthenticatedSuccessfully(object):
        """returned from read when this object is successfully authenticated"""

    def __init__(self, channel, pdbhelper):
        """
        @param pdbhelper: Class that can help us with authenticating users
        """
        JSONSocket.__init__(self, channel)

        self.login = None       #: login
        self.pid = None
        self.pdbhelper = pdbhelper

        self.signed_authentication_off = None  #: whether self.AuthenticatedSuccessfully
                                               # was returned so far
                                               # None if do nothing
                                               # False is next read should return
                                               #    self.AuthenticatedSuccessfully
                                               # True if do nothing

    def on_readable(self):
        JSONSocket.on_readable(self)

        # Is there any data?
        try:
            data = JSONSocket.read(self, peek=True)
        except DataNotAvailable:
            return

        if self.is_authenticated():
            return  # return without consuming the data

        # it must be authentication. Consume it
        JSONSocket.read(self)

        try:
            login, password = data['login'].encode('utf8'), data['password'].encode('utf8')
        except KeyError:
            self.write({'status': 'fail', 'code': 'Malformed JSON request'})
            self.close()    # failed!
            return            

        # Query
        pid, code = self.pdbhelper.authenticate(login, password)

        if code == 0:   # Valid.        
            self.write({'status': 'ok'})
            self.signed_authentication_off = False
            self.login = login
            self.pid = pid
        elif pid == -2: # Banned. TODO: transmit end of ban date
            self.write({'status': 'fail', 'code': 'TODO: banned'})
        elif pid == -1: # Invalid credentials
            self.write({'status': 'fail', 'code': 'Invalid credentials'})

    def read(self):
        """Nonblocking, nonpeeking only"""
        if self.signed_authentication_off == False:
            self.signed_authentication_off = True
            return self.AuthenticatedSuccessfully()            
        else:
            k = JSONSocket.read(self)
            return k

    def is_authenticated(self):
        """Returns whether this socket corresponds to an authorized player"""
        return self.login != None