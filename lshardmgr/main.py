from sys import argv
from threading import Lock
import json
from lshardmgr.master_comms import MasterCommunications
from lshardmgr.spawnobject import SpawnObject

class MainClass(object):
    def __init__(self):
        with open(argv[1], 'rb') as infile:
            data = json.load(infile)

        self.monitor = Lock()

        self.master_comms = MasterCommunications(self, (data['master_host'], data['master_port']), data['id_name'])
        self.id_name = data['id_name']
        self.outside_visible_interface = data['outside_visible_shard_interface']
        self.target_shard_number = data['starting_shards']
        self.tmp_root = data['oper_directory']
        self.sakura_popen = data['sakura_popen']
        self.shards = []

        self.statistics_interface = data['statistics_host'], data['statistics_port']

        self.guidp = 0
        self.available_ports = range(data['shard_ports'][0], data['shard_ports'][0]+data['shard_ports'][1])

        self.master_comms.start()

    def can_allocate_shard(self):
        with self.monitor:
            return len(self.shards) < self.target_shard_number

    def wait_for_shards(self):
        """Return those shard objects that have been completed - they have been poll()ed but not free()d"""
        with self.monitor:
            running_shards = []
            done_shards = []
            for shard in self.shards:
                if shard.poll():
                    done_shards.append(shard)
                    shard.free()
                else:
                    running_shards.append(shard)

            self.shards = running_shards
            return done_shards

    def start_new_shard(self, bpf_chunk, gugid):
        """Return TCP and UDP port"""
        with self.monitor:
            shrd = SpawnObject(self, bpf_chunk, gugid)
            shrd.start()
            self.shards.append(shrd)
            return shrd.tcp_port, shrd.udp_port

    def allocate_ports(self):
        """called by SpawnObject while locked by start_new_shard"""
        if len(self.available_ports) < 2:
            raise Exception, 'Cannot allocate: no ports'
        p1 = self.available_ports[0]
        p2 = p1
        del self.available_ports[0]
        return p1, p2

    def release_port(self, port):
        self.available_ports.append(port)

    def getguid(self):
        """called by SpawnObject while locked by start_new_shard"""
        self.guidp += 1
        return self.guidp-1