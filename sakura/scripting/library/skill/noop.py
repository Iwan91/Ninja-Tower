class Skill(object):
    def __init__(self, invoker, *args):
        pass

    def on_cast_alive(self, gameworld, tx, ty, tpid): pass
    def on_cast_dead(self, gameworld, tx, ty, tpid): pass
    def on_tick(self, gameworld): pass
    def on_silence(self, gameworld): pass