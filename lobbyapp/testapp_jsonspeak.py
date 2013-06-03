from lobbyapp.socketage.sockets import JSONSocket
from socket import SOCK_STREAM, AF_INET, socket
from ssl import wrap_socket

class PlayerSocket(JSONSocket):
    def fail(self):
        print 'CONNECTION CLOSED'

    def on_json(self, data):
        print 'RECVD: %s' % repr(data)    

csock = socket(AF_INET, SOCK_STREAM)
csock = wrap_socket(csock)
csock.settimeout(10)
csock.connect(('91.192.167.227', 5998))
csock = PlayerSocket(csock)

csock.send({'login': 'root', 'password': 'root'})
csock.on_write()

while True:
    csock.on_read()
