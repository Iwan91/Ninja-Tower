import sys
import json
from sakura.instrumentation import log

def load_bpf():
    log('sakura.config.bpf.load_bpf: Compiling BPF')
    with open(sys.argv[1]) as f:
        data = json.load(f)

    d = {'tcp_bind': (data['tcp_interface'], data['tcp_port']),
         'udp_bind': (data['udp_interface'], data['udp_port']),
         'map': data['map_name'],
         'map_name': data['map_name']
         }

    players = {}
    for pid, player in enumerate(data['players']):
        player['pid'] = pid
        players[pid] = player

    d['players'] = players

    return d


    