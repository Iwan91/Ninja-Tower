from __future__ import division
from math import hypot
from sakura.scripting.library.skill.noop import Skill as BaseSkill

class Skill(BaseSkill):
    def __init__(self, invoker, *args):
        self.invoker = invoker

    def on_cast_alive(self, gameworld, tx, ty, tpid):
        self.invoker.on_damage(1000)
