import sys
from sakura.instrumentation import log

registry = {}

from sakura.config.bpf import load_bpf
from sakura.config.map import load_map
from sakura.config.hero import load_hero
from sakura.config.shot import load_shot

def init():
    global registry
    log('sakura.config: Beginning config compilation')

    # Load baseline data
    registry = load_bpf()

    # Load game map
    registry['map'] = load_map(registry['map'])

    shots_to_load = set()

    # Load player characters
    for pid, player_profile in registry['players'].iteritems():
        player_profile['character'] = load_hero(player_profile['character'])
        for shot in player_profile['character']['related_shots']:
            shots_to_load.add(shot)

    # Load shots
    registry['shots'] = {}
    for shot in shots_to_load:
        try:
            registry['shots'][int(shot)] = load_shot(shot)
        except:
            raise
            print 'sakura.config.__init__: Could not load shot %s' % (shot, )


    registry['_runtime'] = {}
