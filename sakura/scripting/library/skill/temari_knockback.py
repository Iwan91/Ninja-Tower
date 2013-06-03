from sakura.config import registry
from sakura.scripting.library.skill.noop import Skill as BaseSkill
from sakura.players.meta import MetaShotSupportingClass
from sakura.physics.base import Shot
from sakura.scripting import mathops

class Knockback(MetaShotSupportingClass):
    shot_type = 3
    def __init__(self, damage, pushbackforce, ros, team):
        self.damage = damage
        self.push_force = pushbackforce
        self.ros = ros
        self.live = True
        self.ttl = 250
        self.already_encountered = []       # who has been pushed back so far
    def on_tick(self, gameworld):
        MetaShotSupportingClass.on_tick(self, gameworld)
        self.ttl -= 1
    def on_obstacle(self, obstacle): pass
    def on_boundary(self, mapboundary): self.live = False
    def wants_removal(self): return (self.ttl == 0) or (not self.live)
    def on_actor(self, actor):
        if actor in self.already_encountered: return
        self.already_encountered.append(actor)
        actor.meta.on_damage(self.damage)

        # push back the actor
        vx, vy = mathops.vector_towards(actor.x, actor.y, self.shot.x, self.shot.y, self.push_force)
                # apply the vector in reverse (AWAY from invoker)
        actor.dx -= vx
        actor.dy -= vy

        actor.meta.ministun += self.ros
        actor.no_anchor += self.ros
        actor.meta.on_stunned()

class Skill(BaseSkill):
    def __init__(self, invoker, damage, speed, pushback, ros, *args):
        self.damage = float(damage)
        self.ros = int(ros)
        self.pushback = float(pushback)
        self.speed = float(speed)
        self.invoker = invoker

        self.drop_on = -100

    def on_silence(self, gameworld):
        self.drop_on = -100

    def on_tick(self, gameworld):
        if not self.invoker.alive: return
        if self.drop_on == gameworld.iteration:
            actor = self.invoker.actor

            xdir = 1 if actor.direction == 0 else -1

            sh = Shot(registry['shots'][3]['animations'], actor.x+(3*xdir), actor.y-5, self.speed*xdir, 0, self.invoker.team, Knockback(self.damage, self.pushback, self.ros, self.invoker.team))
            gameworld.on_sd_register_shot(sh)

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        self.drop_on = gameworld.iteration + 34

        gameworld.on_sd_skill_deployed(self.invoker.pid, 8)
