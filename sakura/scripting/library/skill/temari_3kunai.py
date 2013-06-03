from sakura.config import registry
from sakura.scripting.library.skill.noop import Skill as BaseSkill
from sakura.players.meta import MetaShotSupportingClass
from sakura.physics.base import Shot
from sakura.scripting import mathops

class Kunai(MetaShotSupportingClass):
    shot_type = 1
    def __init__(self, damage, team):
        self.damage = damage
        self.live = True
    def on_obstacle(self, obstacle): self.live = False
    def on_boundary(self, mapboundary): self.live = False
    def wants_removal(self): return not self.live
    def on_actor(self, actor):
        actor.meta.on_damage(self.damage)
        self.live = False

class Skill(BaseSkill):
    def __init__(self, invoker, damage, speed, *args):
        self.damage = float(damage)
        self.speed = float(speed)
        self.invoker = invoker

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        actor = self.invoker.actor
        va = mathops.vector_towards(actor.x, actor.y, tx, ty-30, self.speed)
        vb = mathops.vector_towards(actor.x, actor.y, tx, ty, self.speed)
        vc = mathops.vector_towards(actor.x, actor.y, tx, ty+30, self.speed)
        if vb == None: return

        xdir = 1 if actor.direction == 0 else -1

        sh = Shot(registry['shots'][1]['animations'], actor.x+(5*xdir), actor.y-5, va[0], va[1], self.invoker.team, Kunai(self.damage, self.invoker.team))
        gameworld.on_sd_register_shot(sh)

        sh = Shot(registry['shots'][1]['animations'], actor.x+(5*xdir), actor.y-5, vb[0], vb[1], self.invoker.team, Kunai(self.damage, self.invoker.team))
        gameworld.on_sd_register_shot(sh)

        sh = Shot(registry['shots'][1]['animations'], actor.x+(5*xdir), actor.y-5, vc[0], vc[1], self.invoker.team, Kunai(self.damage, self.invoker.team))
        gameworld.on_sd_register_shot(sh)

        gameworld.on_sd_skill_deployed(self.invoker.pid, 5)

