from sakura.instrumentation import log

import json
import sys
import time

import sakura.config
import sakura.network
import sakura.gameworld
import sakura.players
import sakura.physics

if __name__ == '__main__':
    log('sakura: Sakura v1.0 starting')
    log('sakura: Compiling configuration')

    sakura.config.init()

    log('sakura: Initializing network layer')

    sakura.network.init_sockets()
    sakura.network.init_sequencer()
    sakura.network.init_network()

    log('sakura: Initializing game world objects')
    sakura.physics.init_simulation()
    sakura.players.init_delegates()

    log('sakura: Starting game world simulation')

    sakura.gameworld.init_gameworld()


    try:
        # following blocks until the game is over
        sakura.config.registry['game_world_processor'].run()
    except sakura.gameworld.GameFinishedException as gfx:

        with open(sys.argv[3], 'wb') as rtv:
            # check what is the victory mode?
            if gfx.winner == None:
                # essentially nobody won
                if gfx.cc == sakura.gameworld.GameFinishedException.CC_NOBODY_LOGGED_IN:
                    json.dump({'status': 'abnormal', 'reason': 'nobody logged in'}, rtv)    
            else:
                json.dump({'status': 'victory', 'reason': 'points', 'winner': gfx.winner}, rtv)            

        time.sleep(5)
        sakura.config.registry['game_world_processor'] = False # network thread detects this and aborts
        sakura.config.registry['_runtime']['select_loop_thread'].join()  # wait for network thread
        # closing time

        log('sakura: Terminating')
        sys.exit(0)  
