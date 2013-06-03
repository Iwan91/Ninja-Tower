from time import sleep
import json
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from satella.threads import BaseThread

from satella.channels.sockets import ServerSocket
from satella.instrumentation import CounterCollection

from satella.instrumentation.exctrack import Trackback

from cshardmgr.selectloop import SelectLayer

if __name__ == '__main__':
    
    # Perform master initialization, reading the config JSON file
    with open(argv[1], 'r') as k:
        config = json.load(k)

    # --------------------------------------------- Instrumentation root
    nsm = CounterCollection('cshardmgr')

    # -------------------------------------------- Socket interfacing part!

    # Read and initialize socket server interface
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((config['univ_listening_interface'], config['univ_listening_port']))
    server_socket.listen(10)
    server_socket = ServerSocket(server_socket)

    # Do the server layer
    handling_layer = SelectLayer([server_socket], nsm)

    # ===================================================== Core run option

    from satella.instrumentation.exctrack import Trackback

    # ----- designate runner threads

    class SLThread(BaseThread):
        def run(self):
            try:
                while not self._terminating:
                    handling_layer.select(timeout=1)
            except:
                print Trackback().pretty_print()

    # ----- fire'em
    t_phl = SLThread().start()


    # ---- instrumentation BHTIPI ;)
    from satella.contrib.bhtipi import BHTIPI
    bhtipi = BHTIPI('0.0.0.0', 8081, nsm, True).start()

    from time import sleep
    while True:
        sleep(1000)

    # --- terminate stuff

    s = list([x.terminate() for x in [t_phl, t_ep, bhtipi, omm, ac]])
    for x in s: s.join()
