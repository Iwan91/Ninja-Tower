from time import sleep
import json
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from ssl import wrap_socket
from satella.threads import BaseThread

from satella.channels.sockets import SSLServerSocket, ServerSocket
from satella.instrumentation import CounterCollection
from Queue import Queue

from lobbyapp.selectlayer import PlayersHandlingLayer
from lobbyapp.dbmangr import DatabaseManager
from lobbyapp.selectlayer.api import PDBHelperInterface as SelectLayerPDBHelper
from lobbyapp.playerdb.api import PDBHelperInterface as PlayerDBPDBHelper

from lobbyapp.queuemangr import QueueManager, OpportunisticMatchMaker, AlphaCounter
from lobbyapp.playerdb import PlayerDatabase
from lobbyapp.statisticsnotary import StatisticsNotary
from lobbyapp.eventprocessor import EventProcessor

if __name__ == '__main__':
    
    # Perform master initialization, reading the config JSON file
    with open(argv[1], 'r') as k:
        config = json.load(k)

    # --------------------------------------------- Instrumentation root
    nsm = CounterCollection('lobbyapp')


    # Set up master database connection
    database_manager = DatabaseManager(config['sqldb_host'],
                                       config["sqldb_username"],
                                       config["sqldb_password"],
                                       config["sqldb_dbname"],
                                       nsm,
                                       dbtype='mysql')

    # -------------------------------------------- Socket interfacing part!

    # Read and initialize socket server interface
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((config['inbound_listening_interface'], config['inbound_listening_port']))
    server_socket.listen(10)
    server_socket = wrap_socket(server_socket, 
                                config['inbound_keyfile'],
                                config['inbound_certfile'],
                                True)
    server_socket = SSLServerSocket(server_socket)


    # ===================================================== SelectLayer
    # ------------ comms from and to EventProcessor
    SLtoEP, EPtoSL = Queue(), Queue()

    # Set up player handling layer
    players_handling_layer = PlayersHandlingLayer(server_socket, 
                                                  SLtoEP, 
                                                  EPtoSL, 
                                                  database_manager.query_interface(SelectLayerPDBHelper),
                                                  nsm)

    # ===================================================== In-lobby stuff management
    qmgr = QueueManager(config['queues'], nsm)


    # ===================================================== PlayerDB
    player_database = PlayerDatabase(database_manager.query_interface(PlayerDBPDBHelper),
                                     nsm,
                                     qmgr,
                                     SLtoEP,
                                     (
                                        config['cshard_outbound_interface'],
                                        config['cshard_outbound_port'],
                                     ))
 

    # ===================================================== queue workers
    omm = OpportunisticMatchMaker(player_database, nsm).start()
    ac = AlphaCounter(player_database, nsm).start()

    # ===================================================== EventProcessor
    ep = EventProcessor(player_database, EPtoSL, SLtoEP, nsm)

    # ===================================================== StatisticsNotary

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((config['stat_not_interface'], config['stat_not_port']))
    server_socket.listen(10)    
    server_socket = ServerSocket(server_socket)

    sn = StatisticsNotary(player_database, server_socket)

    # ===================================================== Core run option

    from satella.instrumentation.exctrack import Trackback

    # ----- designate runner threads


    class SNThread(BaseThread):
        def run(self):
            while not self._terminating:
                try:
                    sn.select(timeout=10)
                except:
                    with open('testlog', 'ab') as x:
                        x.write(Trackback().pretty_print()+'\n')

    class PHLThread(BaseThread):
        def run(self):
            while not self._terminating:
                try:
                    players_handling_layer.select(timeout=1)
                except:
                    with open('testlog', 'ab') as x:
                        x.write(Trackback().pretty_print()+'\n')

    class EPThread(BaseThread):
        def run(self):
            while not self._terminating:
                try:
                    ep.process()
                except:
                    print Trackback().pretty_print()                    

    print 'basic threads started'

    # ----- fire'em
    t_phl = PHLThread().start()
    t_ep = EPThread().start()
    t_sn = SNThread().start()

    # ---- instrumentation BHTIPI ;)
    from satella.contrib.bhtipi import BHTIPI
    bhtipi = BHTIPI('0.0.0.0', 8080, nsm, True).start()

    # ---- hang here

    from time import sleep
    while True:
        sleep(1000)

    # --- terminate stuff

    s = list([x.terminate() for x in [t_phl, t_ep, bhtipi, omm, ac, t_sn]])
    for x in s: s.join()
