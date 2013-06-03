from lobbyapp.selectlayer.api import DataArrived, PlayerOnline, PlayerOffline, SendData
from lobbyapp.eventprocessor.api import MatchFound, MatchDodged, HeroPicked, PlayerLockedIn, \
                                        MatchOKAndWillStart, MatchFAILED, ForceToMatch, \
                                        MatchEnded

from lobbyapp.playerdb.transactions import *

class EventProcessor(object):
    def __init__(self, pdb, to_selectlayer, from_selectlayer, rootcc):
        """
        @type to_selectlayer: L{Queue.Queue}
        @type from_selectlayer: L{Queue.Queue}
        """        
        self.pdb = pdb
        self.to_selectlayer = to_selectlayer
        self.from_selectlayer = from_selectlayer
        self.rootcc = rootcc


    def send_general_failpacket(self, pid, msg):
        """sends a generic fail + message packet to given pid"""
        self.to_selectlayer.put(SendData(pid, {
                'status': 'fail',
                'code': msg
            }))        


    def process(self):
        """Perform a round of processing events.
        Will hang waiting on an event to arrive"""

        evt = self.from_selectlayer.get()

        if isinstance(evt, PlayerOnline):   # player went online            
            TRPlayerOnline(self.pdb, evt.pid).start()            
        elif isinstance(evt, PlayerOffline):
            TRPlayerOffline(self.pdb, evt.pid).start()
        elif isinstance(evt, DataArrived):
            if evt.data['operation'] == 'enqueue':                      # wants to join a queue
                # check if applies to join a queue
                if not self.pdb.applies_for_queue(evt.pid):
                    self.send_general_failpacket(evt.pid, 'not applicable')
                    return

                # check if given queue exists
                if not self.pdb.qmangr.has_queue(evt.data['gametype']):
                    self.send_general_failpacket(evt.pid, 'queue not exists')
                    return

                # ok, enqueue him
                if TREnqueue(self.pdb, evt.pid, evt.data['gametype']).start() == False:
                    self.send_general_failpacket(evt.pid, 'transaction failed')
                else:
                    self.to_selectlayer.put(SendData(evt.pid, {'status': 'ok'}))
            elif evt.data['operation'] == 'dequeue':
                # check if applies. Transaction will fail if not enqueued
                if TRDequeue(self.pdb, evt.pid).start() == False:
                    self.send_general_failpacket(evt.pid, 'transaction failed')
                else:
                    self.to_selectlayer.put(SendData(evt.pid, {'status': 'ok'}))
            elif evt.data['operation'] == 'dodge':
                if TRMatchDodge(self.pdb, evt.pid).start() == False:
                    self.send_general_failpacket(evt.pid, 'transaction failed')
                else:
                    self.to_selectlayer.put(SendData(evt.pid, {'status': 'ok'}))
            elif evt.data['operation'] == 'match_pick':
                if 'hero' not in evt.data:
                    self.send_general_failpacket(evt.pid, 'malformed request')

                k = TRHeroPick(self.pdb, evt.pid, evt.data['hero']).start()
                if k == False:
                    self.send_general_failpacket(evt.pid, 'transaction failed')                    
                elif k == 2:
                    self.send_general_failpacket(evt.pid, 'already picked')                    
                else:
                    self.to_selectlayer.put(SendData(evt.pid, {'status': 'ok'}))
            elif evt.data['operation'] == 'hero_lock_in':
                k = TRLockIn(self.pdb, evt.pid).start()
                if k == False:
                    self.send_general_failpacket(evt.pid, 'transaction failed')
                elif k == 2:
                    self.send_general_failpacket(evt.pid, 'hero not picked')
                else:
                    self.to_selectlayer.put(SendData(evt.pid, {'status': 'ok'}))
            elif evt.data['operation'] == 'server_statistics':
                #                       get server statistics
                # get how-many-players-in-queue
                queues = {}
                for queue in self.rootcc.get('queues').get():
                    queues[queue.name] = queue.get('players').get_current()

                # get how many players logged in
                jsonobj = {
                    'status': 'server_statistics',
                    'players_in_queue': queues,
                    'players_online': self.rootcc.get('selectlayer').get('connections').get_current(),
                    }
                self.to_selectlayer.put(SendData(evt.pid, jsonobj))


        elif isinstance(evt, MatchFound):
            # match was found for players
            jsonobj = {
                'status': 'match_found',
                'team1': evt.team1,
                'team2': evt.team2,
                'qname': evt.qname,
                'heroes': evt.heroes
            }

            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, MatchDodged):  
            # sent to victim of a dodge
            jsonobj = {
                'status': 'dodge_victim',
                'qname': evt.queue
            }
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, HeroPicked):
            jsonobj = {
                'status': 'hero_picked',
                'login': evt.login,
                'hero': evt.hero
            }
            print 'Hero picked -> %s with (%s, %s)' % (evt.pid, evt.login, evt.hero)
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, PlayerLockedIn):
            jsonobj = {
                'status': 'hero_locked_in',
                'login': evt.login
            }
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, MatchOKAndWillStart):
            jsonobj = {
                'status': 'match_starting',
                'condition': 'ok',
                'target_ip': evt.target_ip,
                'target_port_tcp': evt.target_port_tcp,
                'target_port_udp': evt.target_port_udp
            }
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, MatchFAILED):
            jsonobj = {
                'status': 'match_starting',
                'condition': 'fail',
                'code': evt.code
            }
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, ForceToMatch):
            jsonobj = {
                'status': 'request_to_reconnect',
                'target_ip': evt.target_ip,
                'target_port_tcp': evt.target_port_tcp,
                'target_port_udp': evt.target_port_udp
            }
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))
        elif isinstance(evt, MatchEnded):
            jsonobj = {
                'status': 'round_ended',
                'victor': evt.victor,
                'mof': evt.mof,
                'last_round': evt.last_round
            }
            self.to_selectlayer.put(SendData(evt.pid, jsonobj))