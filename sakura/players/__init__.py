from __future__ import division
from time import time
from sakura import config
from sakura.instrumentation import log
from sakura.players.meta import MetaActorSupportingClass
from sakura.network.sequencer import MsgKbdStateUpdate, MsgSkillKeyDeployed, \
                                     MsgPlayerOnline, MsgPlayerOffline
from sakura.physics.base import Actor
from sakura.gameworld.repllog import ReportPlayerDied, ReportPlayerRevived

from sakura.buffs.base import BuffSystem

IOCM_LIMIT = 0

class StatusDelegate(MetaActorSupportingClass):
    def __init__(self, pid):
        self.buffs = BuffSystem()

        self.pid = pid
        self.keyboard = (False, False, False, False) # Up, Right, Down, Left
        self.gameworldprocessor = None  #: to be filled in by GameWorldProcessor

        self.hero_archetype = config.registry['players'][pid]['character']
        self.player_archetype = config.registry['players'][pid]

        self.max_hp = self.hero_archetype['hp']
        self.base_regen = self.hero_archetype['regen']
        self.base_speed = self.hero_archetype['speed']

        self.regen, self.speed = self.base_regen, self.base_speed

        self.online = False
        self.alive = False

        self.team = self.player_archetype['team']
        self.jump = self.hero_archetype['jump']

        self.actor = None
        self.ministun = 0   # number of iterations for which keyboard won't respond

        self.dead_countdown = 0

        self.iocm = 0   # iterations of consecutive vertical movement

        # ------------------ Skill support
        self.skills = [None, None, None, None, None]
        self.can_cast_on = [0, 0, 0, 0, 0]
        self.cooldowns = [None, None, None, None, None]
        # Init skill table
        for keyid in xrange(0, 5):
            self.cooldowns[keyid] = self.hero_archetype['skilltab'][keyid][0]
            self.skills[keyid] = self.hero_archetype['skilltab'][keyid][1](self)

    def recalculate_buffs(self):
        """called by GameWorldProcessor if it detects that we need to refresh our buffs"""
        print 'recalculating buffs'
        self.regen, self.speed = self.buffs.calculate(self.base_regen, self.base_speed)

    def on_apply_buff(self, buff):
        self.buffs.apply(buff)
        self.recalculate_buffs()

    def _bring_me_to_life(self):        # creates an actor and registers it against GameWorld
        """Internal helper to create a live actor that represents us"""
        self.alive = True
        x, y = config.registry['map']['spawnpoints'][self.team]
        self.actor = Actor(self.hero_archetype['animations'], x, y, self.team, self)
        self.hp = self.max_hp
        self.gameworldprocessor.on_sd_register_actor(self.actor)
        self.gameworldprocessor.repllog.append(ReportPlayerRevived(self.pid))


    def on_silenced(self):
        """Invoked by skill handlers when character gets silenced"""
        for skill in self.skills:
            skill.on_silence(self.gameworldprocessor)

    def _oh_my_goddess_im_dead(self, scored=True):
        self.alive = False
        self.actor = None   # he will be slain later by Simulation according to our flags
        if scored:
            self.gameworldprocessor.repllog.append(ReportPlayerDied(self.pid))
            self.dead_countdown = 5*40
            self.on_silenced()

    def on_damage(self, damage):
        """
        CALLED BY: Skills and shot handlers
        Damage has been inflicted upon the player
        """
        if not self.alive: return
        self.hp -= damage
        if self.hp <= 0:
            # Critical existence failure
            self._oh_my_goddess_im_dead()
            self.gameworldprocessor.on_sd_actor_dead(self)
            self.hp = 0

    def on_heal(self, heal):
        """
        CALLED BY: Skills and shot handlers
        Heal has been inflicted upon the player
        """
        self.hp += heal
        if self.hp > self.max_hp: self.hp = self.max_hp

    # ------------------------------------- Called by GameWorldProcessor, friends and relatives
    def on_apply_gravity(self, amount_requested):
        """
        CALLED BY: GameWorldProcessor/Simulation
        Physics processor wants to apply amount_requested gravity to us
        """
        self.actor.dy += amount_requested

    def on_apply_changes(self):
        """
        CALLED BY: GameWorldProcessor
        Executed each loop at a particular time in GameWorldProcessor
        """

        for skill in self.skills:
            if skill == None: continue
            skill.on_tick(self.gameworldprocessor)

        if not self.online: return

        if not self.alive:
            self.dead_countdown -= 1
            if self.dead_countdown == 0:
                self._bring_me_to_life()
        else:

            prev_dx = self.actor.dx

            # Reduce no_anchor
            if self.actor.no_anchor: self.actor.no_anchor -= 1
            # HP regen
            if self.hp < self.max_hp:
                self.hp += self.regen
                if self.hp > self.max_hp:
                    self.hp = self.max_hp
            if self.ministun > 0:
                self.ministun -= 1
            else:
                target_dx = 0

                self.actor.h_moving = self.keyboard[1] or self.keyboard[3]

                if self.keyboard[1]:
                    target_dx = self.speed
                    self.actor.direction = 0
                if self.keyboard[3]:
                    target_dx = -self.speed
                    self.actor.direction = 1
                if self.keyboard[2]:
                    self.actor.no_anchor += 1
                if self.keyboard[0] and self.actor.v_braked:
                    self.actor.dy = -self.jump

                if not self.actor.h_moving:
                    self.iocm = 0
                else:
                    self.iocm += 1

                if self.iocm < IOCM_LIMIT: target_dx = target_dx/2

                diff = self.actor.dx - target_dx
                if abs(diff) < self.speed:
                    self.actor.dx = target_dx
                elif diff < 0:
                    self.actor.dx += self.speed
                elif diff > 0:
                    self.actor.dx -= self.speed

            if (prev_dx == 0) and (self.actor.dx != 0):
                # actor has started moving
                self.actor.on_start_horizontal_movement()
            elif (prev_dx != 0) and (self.actor.dx == 0):
                self.actor.on_stop_horizontal_movement()

            self.actor.autopick_geometry()

            self.actor.is_on_roof = False

    # On rapports from sequencer
    def on_sequencer(self, sqmsg):
        """We have received a command for this character via sequencer"""
        sqk = type(sqmsg)
        if sqk == MsgKbdStateUpdate:
            self.keyboard = sqmsg.kbd
        elif sqk == MsgPlayerOnline:
            self.keyboard = (False, False, False, False)
            if not self.online:
                self.online = True
                self._bring_me_to_life()
        elif sqk == MsgPlayerOffline:
            self.online = False
            self._oh_my_goddess_im_dead(scored=False)
        elif sqk == MsgSkillKeyDeployed:
            qkid = sqmsg.qkid
            tx, ty, tpid = sqmsg.x, sqmsg.y, sqmsg.target

            if time() < self.can_cast_on[qkid]: return  # Spell is on cooldown
            if self.alive:
                self.skills[qkid].on_cast_alive(self.gameworldprocessor, tx, ty, tpid)
            else:
                self.skills[qkid].on_cast_dead(self.gameworldprocessor, tx, ty, tpid)

            self.can_cast_on[qkid] = time() + self.cooldowns[qkid]

    # --------------------------------------------------- MetaActorSupportingClass overrides
    def wants_removal(self):
        x = not (self.online and self.alive)
        return x

def init_delegates():
    delegates = {}
    log('sakura.players.init_delegates: Initializing status delegates')
    for pid_or_login, player in config.registry['players'].iteritems():
        if type(pid_or_login) in (int, long):
            delegates[pid_or_login] = StatusDelegate(pid_or_login)    

    config.registry['_runtime']['status_delegates'] = delegates