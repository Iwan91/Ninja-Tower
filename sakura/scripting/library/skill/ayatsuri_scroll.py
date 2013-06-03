from sakura.config import registry
from sakura.scripting.library.skill.noop import Skill as BaseSkill
from sakura.players.meta import MetaShotSupportingClass
from sakura.physics.base.primitives import Rectangle
from sakura.physics.base import Shot
from sakura.gameworld.cfsf import CFSF
from sakura.scripting import mathops

CAST_EFFECT_DELAY = 20

ANIM2_EXPIRATION = 55
class Scroll(MetaShotSupportingClass):
    shot_type = 6
    def __init__(self, damage, team):
        self.team = team
        self.damage = damage
        self.live = True
        self.sticked = False
        self.delta_stick = None #: tuple (x, y) to actor that can help maintain distance
        self.actor_sticked_to = None
        self.direction_sticked = None
        self.expires_on = None
    def on_obstacle(self, obstacle):
        self.live = False
    def on_boundary(self, mapboundary):
        self.live = False
    def wants_removal(self): return not self.live

    def on_tick(self, gameworld):
        """Called on each iteration. Shot is this shot"""
        if not self.sticked:
            if self.shot.dx >= 0:
                self.shot.pick_geometry(0)
            else:
                self.shot.pick_geometry(1)
        else:
            self.shot.pick_geometry(2+self.direction_sticked)

        if self.sticked:
            self.shot.x = self.delta_stick[0] + self.actor_sticked_to.x
            self.shot.y = self.delta_stick[1] + self.actor_sticked_to.y

            self.expires_on -= 1
            if self.expires_on == 0: self.live = False

            if self.expires_on == 40:
                if self.direction_sticked == 0: # right
                    impakt_radius = Rectangle(0, 0, 60, 39)
                else:   # left
                    impakt_radius = Rectangle(-60, -39, 0, 9)

                cfs = CFSF(gameworld)
                actors = cfs.actor_rect_notteam(impakt_radius, self.team, self.shot.x, self.shot.y)
                for actor in actors:
                    actor.meta.on_damage(self.damage)

            self.shot.dx, self.shot.dy = self.actor_sticked_to.dx, self.actor_sticked_to.dy

    def on_actor(self, actor):
        if self.team == actor.meta.team: return
        if self.sticked: return

        self.sticked = True

        # back if off by two-three iterations
        self.shot.x -= self.shot.dx
        self.shot.y -= self.shot.dy

        # lock in delta
        self.delta_stick = self.shot.x - actor.x, self.shot.y - actor.y
        self.actor_sticked_to = actor

        self.direction_sticked = self.shot.animation_id % 2

        self.shot.dx, self.shot.dy = actor.dx, actor.dy

        self.expires_on = ANIM2_EXPIRATION

class Skill(BaseSkill):
    def __init__(self, invoker, damage, speed, *args):
        self.damage = float(damage)
        self.speed = float(speed)
        self.invoker = invoker

        self.scroll_geometry_set = registry['shots'][6]['animations']
        self.cast_on = None

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        self.cast_on = gameworld.iteration + CAST_EFFECT_DELAY
        gameworld.on_sd_skill_deployed(self.invoker.pid, 10)

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

        sh = Shot(self.scroll_geometry_set, actor.x+(28*xdir), actor.y-17, vt[0], vt[1], self.invoker.team, Scroll(self.damage, self.invoker.team))

        gameworld.on_sd_register_shot(sh)
