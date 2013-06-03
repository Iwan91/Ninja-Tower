from __future__ import division
from threading import Thread
from sakura import config
from Queue import Empty
from sakura.network.sequencer import MsgKbdStateUpdate, MsgSkillKeyDeployed, \
                                     MsgPlayerOnline, MsgPlayerOffline
from sakura.gameworld.sidallocator import SIDAllocator
from sakura.gameworld.repllog import ReportShotDestroyed, ReportTrackedShotCreated, \
                                     ReportUntrackedShotCreated, ReportPlayerHPChanged, \
                                     ReportSkillDeployed, ReportBuffStatus
from sakura.gameworld.cfsf import CFSF
from time import time, sleep
import heapq
from collections import defaultdict

GAME_STARTS_ON = 100        # in Iterations
NOBODY_LOGGED_IN_CUTOFF = 3000000 #12000 # in Iterations - grace period to log in

EPSILON_LENGTH = 0.025       # in Seconds
KILL_LIMIT = None         # first one to score KILL_LIMIT wins

class GameFinishedException(Exception):

    CC_NOBODY_LOGGED_IN = 0

    def __init__(self, team_that_won, cc=None):
        self.winner = team_that_won
        self.cc = None

class GameWorldProcessor(Thread):
    def __init__(self):

        global KILL_LIMIT
        KILL_LIMIT = len(config.registry['_runtime']['status_delegates'])*2

        Thread.__init__(self)
        self.physics = config.registry['_runtime']['simulation']
        self.delegates = config.registry['_runtime']['status_delegates']
        for delegate in self.delegates.itervalues():
            delegate.gameworldprocessor = self
        self.sequencer = config.registry['_runtime']['sequencer']
        self.iteration = 0
        self.sidallocator = SIDAllocator()
        self.cfsf = CFSF(self)

        self.old_hp = defaultdict(lambda: None)    # used for detection whether HP has changed

        self.game_started = False

        self.score = {0: 0, 1: 0}   # which team has how many kills

        self.averaging_percent_statistics = []

        self.last_time_seen = defaultdict(lambda: 0)    # iteration time the last time somebody
                                                        # from a team was seen

        self.callback_heap = []

    def update_last_time_seen(self):
        for delegate in [x for x in self.delegates.itervalues() if x.online]:
            self.last_time_seen[delegate.team] = self.iteration

    def loop(self):
        """
        Shot overview:
            - Clear REPLLOG
            - Received and dispatch network requests
            - Advance round for players (on tick call)
            - Advance round for shots (on tick call)
            - Perform a round of physics iteration
            - Check for HP change in actors
            - Dispatch REPLLOG entries
            - Send UDP generation 0 to players if necessary
            - Wait for next iteration time

        What is REPLLOG?
            REPLLOG is a list of things that has happened on a single iteration. Instead of sending a 
            TCP packet to everyone that something has changes, we collect all changes on an interation
            and then send them in one shot.
            This saves bandwidth, as we send less packets.
        """
        time_measure = time()

        self.repllog = []       # messages from REPLLog will be aggregated and sent to all players on end of loop

        # Process messages from the sequencer
        try:
            while True:
                pid, msg = self.sequencer.rcvd_commands.get(block=False)
                if not self.game_started:
                    if type(msg) in (MsgKbdStateUpdate, MsgSkillKeyDeployed):
                        continue
                if type(msg) == MsgPlayerOnline:
                    # we should send him current score
                    self.sequencer.send_score(pid, self.score[0], self.score[1])
                self.delegates[pid].on_sequencer(msg)
        except Empty:
            pass

        # Advance round for players
        for delegate in self.delegates.itervalues():
            delegate.on_apply_changes()

        # Advance round for shots
        for shot in self.physics.shots:
            shot.meta.on_tick(self)


        # Check for callbacks
        while len(self.callback_heap) > 0:
            if self.callback_heap[0][0] > self.iteration:
                break
            hp = heapq.heappop(self.callback_heap)
            hp(gameworld)

        self.physics.new_iteration()

        removed_shots, = self.physics.iteration()
        # Process removed shots into REPLLOG records
        for removed_shot in removed_shots:
            if not removed_shot.meta.SHADOW:
                self.repllog.append(ReportShotDestroyed(removed_shot.meta.sid))

        # Check old and new HP - generate REPLLOG entries
        # Check old and new buffs - generate REPLLOG entries
        for pid, delegate in self.delegates.iteritems():
            try:
                if self.old_hp[pid] != int(delegate.hp):
                    self.repllog.append(ReportPlayerHPChanged(pid, int(delegate.hp)))
                    self.old_hp[pid] = int(delegate.hp)
            except AttributeError:                
                pass        # delegate has no HP. Dead or DCed. Do nothing

            new_buffs = delegate.buffs.get_dirty_buffs()
            old_buffs = delegate.buffs.clean()

            if (len(old_buffs)+len(new_buffs)) > 0:
                # Delegate needs to recalculate buffs                
                delegate.recalculate_buffs()

            for buff in new_buffs:
                self.repllog.append(ReportBuffStatus(pid, buff.id, buff.stacks, buff.get_expires_in()))
            for buff in old_buffs:
                self.repllog.append(ReportBuffStatus(pid, buff.id, 0, 0))


        self.iteration += 1

        # ... Process REPLLOG around here ...
        if len(self.repllog) > 0:
            self.sequencer.relay_repllog(''.join([rl.ton() for rl in self.repllog]), self.iteration)
            self.repllog = []       # reset REPLLOG

        # physics done, send packets about status to our folks
        a = []
        if self.iteration % 2 == 0:
            for actor in self.physics.actors:
                if actor._last_sent_d != (actor.dx, actor.dy):
                    actor.packets_to_resend = 3
                if actor.packets_to_resend > 0:
                    actor.packets_to_resend -= 1
                    a.append((actor.animation_id, actor.meta.pid, actor.x, actor.y, actor.dx, actor.dy))
                    actor._last_sent_d = actor.dx, actor.dy

            for shot in self.physics.shots:
                if shot.meta.UNTRACKED: continue
                if shot._last_sent_d != (shot.dx, shot.dy):
                    shot.packets_to_resend = 3
                if shot.packets_to_resend > 0:
                    shot.packets_to_resend -= 1
                    a.append((shot.animation_id+128, shot.meta.sid, shot.x, shot.y, shot.dx, shot.dy))
                    shot._last_sent_d = shot.dx, shot.dy
            self.sequencer.relay_status(a, self.iteration)

        if not self.game_started:
            if self.iteration > GAME_STARTS_ON:
                self.sequencer.relay_game_started()
                self.game_started = True


        self.update_last_time_seen()

        # CHECK VICTORY CONDITIONS
        # ---- point victory
        if self.score[0] >= KILL_LIMIT:
            # Team 0 won
            self.sequencer.send_game_over(0)
            raise GameFinishedException(0)
        elif self.score[1] >= KILL_LIMIT:
            # Team 1 won
            self.sequencer.send_game_over(1)
            raise GameFinishedException(1)
        # ---- sandbox termination
        if len(config.registry['_runtime']['status_delegates']) == 1:
            if self.iteration > 12000:
                self.sequencer.send_game_over(0)
                raise GameFinishedException(0)

        # ---- walkovers
        candidates = []     # candidates to a walkover
        for team in (0, 1):
            if (self.iteration - self.last_time_seen[team]) > NOBODY_LOGGED_IN_CUTOFF:
                candidates.append(team)

        if len(candidates) == 2:
            # walkover, failure
            raise GameFinishedException(None, GameFinishedException.CC_NOBODY_LOGGED_IN)
        elif len(candidates) == 1:
            # single team walkover
            team_that_lost, = candidates
            self.sequencer.send_game_over(1-team_that_lost)
            raise GameFinishedException(1-team_that_lost)

        s = time()
        k = EPSILON_LENGTH-s+time_measure
        if k>0:
#            if len(self.averaging_percent_statistics) == 100:
#                del self.averaging_percent_statistics[0]
#            self.averaging_percent_statistics.append(k/EPSILON_LENGTH)
#            if self.iteration % 100 == 0:
#                avg = sum(self.averaging_percent_statistics)
#                print 'Server slept for %s%% of iteration time' % (avg, )
            sleep(k)

    def run(self):
        while True:
            self.loop()

    # Callbacks that StatusDelegates are allowed to call during GameWorld's calls to them

    def on_sd_actor_dead(self, sd):
        """Not called if players disconnects"""
        self.score[1-sd.team] += 1

    def on_sd_register_actor(self, actor):
        self.physics.actors.append(actor)

    def on_sd_skill_deployed(self, deployer_pid, skill_id):
        self.repllog.append(ReportSkillDeployed(deployer_pid, skill_id))

    def on_sd_register_callback(self, call_on, callback):
        heapq.heappush(self.callback_heap, (call_on, callback))

    def on_sd_register_shot(self, shot):
        shot.meta.sid = self.sidallocator.allocate_sid()
        self.physics.shots.append(shot)

        try:
            shot.meta.UNTRACKED
        except AttributeError:
            shot.meta.UNTRACKED = False

        try:
            shot.meta.SHADOW
        except AttributeError:
            shot.meta.SHADOW = False

        if shot.meta.SHADOW: return

        if shot.meta.UNTRACKED:
            self.repllog.append(ReportUntrackedShotCreated(shot.meta.sid, shot.meta.shot_type,
                                                           shot.x, shot.y, shot.dx, shot.dy,
                                                           shot.animation_id))
        else:
            shot.meta.UNTRACKED = False
            self.repllog.append(ReportTrackedShotCreated(shot.meta.sid, shot.meta.shot_type,
                                                           shot.x, shot.y, shot.dx, shot.dy,
                                                           shot.animation_id))

def init_gameworld():
    config.registry['game_world_processor'] = GameWorldProcessor()
