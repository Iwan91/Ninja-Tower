from sakura.config import registry
from sakura.scripting.library.skill.noop import Skill as BaseSkill
from sakura.players.meta import MetaShotSupportingClass
from sakura.physics.base import Shot
from sakura.scripting import mathops

CAST_EFFECT_DELAY = 20

class Spin(MetaShotSupportingClass):
    shot_type = 5
    def __init__(self, damage, team):
        self.team = team
        self.damage = damage
        self.live = True
        self.damaged_ones = []
    def on_obstacle(self, obstacle):
        self.live = False
    def on_boundary(self, mapboundary):
        self.live = False
    def wants_removal(self): return not self.live
    def on_actor(self, actor):
        if self.team == actor.meta.team: return
        if actor in self.damaged_ones: return
        actor.meta.on_damage(self.damage)
        self.damaged_ones.append(actor)

class Skill(BaseSkill):
    def __init__(self, invoker, damage, speed, *args):
        self.damage = float(damage)
        self.speed = float(speed)
        self.invoker = invoker

        self.spin_geometry_set = registry['shots'][5]['animations']
        self.cast_on = None

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        self.cast_on = gameworld.iteration + CAST_EFFECT_DELAY
        gameworld.on_sd_skill_deployed(self.invoker.pid, 11)

        self.tx = tx
        self.ty = ty

    def on_silence(self, gameworld):
        self.cast_on = None

    def on_tick(self, gameworld):
        if self.cast_on != gameworld.iteration: return None

        actor = self.invoker.actor
        vt = mathops.vector_towards(actor.x, actor.y, self.tx, self.ty, self.speed)
        if vt == None: return

        xdir = 1 if actor.direction == 0 else -1

        sh = Shot(self.spin_geometry_set, actor.x+(28*xdir), actor.y-17, vt[0], vt[1], self.invoker.team, Spin(self.damage, self.invoker.team))

        gameworld.on_sd_register_shot(sh)
