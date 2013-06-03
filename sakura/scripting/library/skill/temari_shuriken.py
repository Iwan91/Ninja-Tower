from sakura.config import registry
from sakura.scripting.library.skill.noop import Skill as BaseSkill
from sakura.players.meta import MetaShotSupportingClass
from sakura.physics.base import Shot
from sakura.scripting import mathops
from sakura.buffs.base import Buff

class Shuriken(MetaShotSupportingClass):
    shot_type = 2
    def __init__(self, damage, team):
        self.team = team
        self.damage = damage
        self.live = True
    def on_obstacle(self, obstacle): self.live = False
    def on_boundary(self, mapboundary): self.live = False
    def wants_removal(self): return not self.live
    def on_actor(self, actor):
        if self.team == actor.meta.team: return
        actor.meta.on_damage(self.damage)
        actor.meta.on_apply_buff(Slow())
        self.live = False

class Skill(BaseSkill):
    def __init__(self, invoker, damage, speed, *args):
        self.damage = float(damage)
        self.speed = float(speed)
        self.invoker = invoker

        self.shuriken_geometry_set = registry['shots'][2]['animations']

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        actor = self.invoker.actor
        vt = mathops.vector_towards(actor.x, actor.y, tx, ty, self.speed)
        if vt == None: return

        xdir = 1 if actor.direction == 0 else -1

        sh = Shot(self.shuriken_geometry_set, actor.x+(5*xdir), actor.y-5, vt[0], vt[1], self.invoker.team, Shuriken(self.damage, self.invoker.team))

        gameworld.on_sd_register_shot(sh)


        gameworld.on_sd_skill_deployed(self.invoker.pid, 6)