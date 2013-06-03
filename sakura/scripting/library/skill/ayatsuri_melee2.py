from sakura.physics.base.primitives import Rectangle, Geometry
from sakura.gameworld.cfsf import CFSF

CAST_EFFECT_DELAY = 10

class Skill(object):
    def __init__(self, invoker, damage, *args):
        self.cast_on = None
        self.invoker = invoker
        self.damage = int(damage)

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        self.cast_on = gameworld.iteration + CAST_EFFECT_DELAY
        gameworld.on_sd_skill_deployed(self.invoker.pid, 14)

    def on_cast_dead(self, gameworld, tx, ty, tpid): pass
    def on_tick(self, gameworld):
        if gameworld.iteration != self.cast_on: return

        # calculate impact rectangle and it's position
        ax, ay = self.invoker.actor.x, self.invoker.actor.y

        ddir = -2*self.invoker.actor.direction + 1  # -1: left, 1: right

        # create hitscan lead object and calculate it's position
        if ddir == -1:  # left
            impactr = Rectangle(-26, -30, 21, 30)
        else: # right
            impactr = Rectangle(-21, -30, 26, 30)
            
        ix, iy = ax + 20*ddir, ay-12

        # get all actors impacted
        csf = CFSF(gameworld)
        for actor in csf.actor_rect_notteam(impactr, self.invoker.team, ix, iy):
            actor.meta.on_damage(self.damage)

    def on_silence(self, gameworld):
        self.cast_on = None