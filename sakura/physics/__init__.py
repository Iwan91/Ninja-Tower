from sakura.physics.world import Simulation
from sakura.instrumentation import log

def init_simulation():
    from sakura import config

    log('sakura.physics.init_simulation: Initializing simulation')
    physics = Simulation(config.registry['map']['map_boundary'],
                         config.registry['map']['platforms'],
                         config.registry['map']['obstacles'])
    config.registry['_runtime']['simulation'] = physics

