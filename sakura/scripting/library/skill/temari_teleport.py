from __future__ import division
from math import hypot
from sakura.scripting.library.skill.noop import Skill as BaseSkill

class Skill(BaseSkill):
    def __init__(self, invoker, tele_length, *args):
        self.tele_length = float(tele_length)
        self.invoker = invoker

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        actor = self.invoker.actor
        # Calculate effective transportation vector
        tvect = tx-actor.x, ty-actor.y
        tvlen = hypot(*tvect)

        if tvlen == 0: return # cannot teleport nowhere
        if tvlen > self.tele_length: # we need to limit it
            # bring tvect up to snuff
            tvect = tvect[0]*self.tele_length/tvlen, tvect[1]*self.tele_length/tvlen
            tvlen = self.tele_length

        fx = tvect[0]/5
        fy = tvect[1]/5

        actor.x += tvect[0]
        actor.y += tvect[1]

        # Check for collisions
        adv = 5
        while gameworld.cfsf.actor_obstacle(actor) or gameworld.cfsf.actor_boundary(actor): 
            actor.x -= fx
            actor.y -= fy
            adv -= 1
            if adv == 0:
                return

        gameworld.on_sd_skill_deployed(self.invoker.pid, 7)
