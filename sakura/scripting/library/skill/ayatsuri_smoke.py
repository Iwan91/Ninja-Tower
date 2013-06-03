CAST_EFFECT_DELAY = 3

from sakura.physics.base.primitives import Rectangle, Geometry
from sakura.gameworld.cfsf import CFSF
from sakura.config import registry
from sakura.players.meta import MetaShotSupportingClass
from sakura.physics.base import Shot
from sakura.buffs.base import Buff

class Slow(Buff):
    def __init__(self):
        Buff.__init__(self, 1, 8)   # 8 seconds slow
        self.speed = 0.7
    def apply(self, *args, **kwargs):
        # it doesn't stack
        Buff.apply(self, *args, **kwargs)
        self.stacks = 1

class SmokeDummy(MetaShotSupportingClass):
    shot_type = 4   # Smoke Ayatsuri
    def wants_removal(self): return True

class Skill(object):
    def __init__(self, invoker, *args):
        self.cast_on = None
        self.invoker = invoker
        self._cache_dummy_geom = {0: Geometry([Rectangle(0, 0, 0, 0)]),
                                  1: Geometry([Rectangle(0, 0, 0, 0)])}

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        self.cast_on = gameworld.iteration + CAST_EFFECT_DELAY
        gameworld.on_sd_skill_deployed(self.invoker.pid, 13)

    def on_cast_dead(self, gameworld, tx, ty, tpid): pass
    def on_tick(self, gameworld):
        if self.cast_on != gameworld.iteration: return

        # get current actor position and direction, to calculate deltas
        ax, ay = self.invoker.actor.x, self.invoker.actor.y

        ddir = -2*self.invoker.actor.direction + 1  # -1: left, 1: right

        # create hitscan lead object and calculate it's position
        hitscanlead = Rectangle(-7, -4, 7, 4)
        hpx, hpy = ax + 28*ddir, ay-19

        # perform a hitscanning
        cfs = CFSF(gameworld)
        target_hit = None
        while not (cfs.rect_boundary(hitscanlead, hpx, hpy) or cfs.rect_obstacle(hitscanlead, hpx, hpy)):
            k = cfs.actor_rect_notteam(hitscanlead, self.invoker.team, hpx, hpy)
            if len(k) > 0:
                # target hit
                target_hit = k[0]
            hpx += ddir*10

        if target_hit == None: return   # no target was hit

        # paint the target with a shot
        smeta = SmokeDummy()
        shot = Shot(
                self._cache_dummy_geom,
                target_hit.x,
                target_hit.y,
                target_hit.dx, target_hit.dy, 0, smeta
            )

        gameworld.on_sd_register_shot(shot)

        target_hit.meta.on_apply_buff(Slow())

    def on_silence(self, gameworld):
        self.cast_on = None