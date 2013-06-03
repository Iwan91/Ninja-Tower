from time import time

class Buff(object):
    def __init__(self, id, duration, stacks=1):
        """@param duration: in seconds"""
        self.id = id            #: buff id, mandatory
        self.started_on = time()            #: mandatory
        self.expire_on = self.started_on + duration     #: mandatory
        self.stacks = 1 #: mandatory

        self.duration = duration

        self.regen = 1
        self.speed = 1

        self.dirty = True

    def apply(self, stacks=1):
        """refresh the buff or increase the stacks"""
        self.expire_on = time() + self.duration
        self.stacks += stacks
        self.dirty = True

    def get_expires_in(self):
        """Get a int in how many deciseconds does the buff expire"""
        return int(self.expire_on*10 - time()*10)

    def on_timeout(self):
        """called when buff is due to be removed by timeout. Return True 
        if you don't want it removed"""
        return False

    def calculate(self, base_regen, base_speed):
        return base_regen*self.regen, base_speed*self.speed

class BuffSystem(object):
    """
    A container class tracking all current buffs/debuffs and their 
    cumulative spread
    """
    def __init__(self):
        self.buffs = []

    def get_dirty_buffs(self):
        """Return a list of buffs, then set their dirty to false.
        used to detect what buffs appeared since iteration
        to send them back via GSDeltas"""
        dbs = []
        for buff in self.buffs:
            if buff.dirty:
                buff.dirty = False
                dbs.append(buff)
        return dbs

    def apply(self, buff):
        """Applies a buff on the character. If buff of given type is already 
        registered, it will be Applied"""
        print 'applying buff'
        if type(buff) in [type(x) for x in self.buffs]:
            bf = [x for x in self.buffs if type(x) == type(buff)][0]
            bf.apply(buff.stacks)
        else:
            self.buffs.append(buff)

    def clean(self):
        """Returns a sequence of buffs removed due to timeout. Those that
        resisted it by returning True from on_timeout won't be"""
        t = time()
        removed = []
        for buff in [x for x in self.buffs if (x.expire_on < t)]:
            if buff.on_timeout() == True:
                pass    # let it live
            else:
                removed.append(buff)

        for rvd in removed:
            self.buffs.remove(rvd)

        return removed


    def calculate(self, base_regen, base_speed):
        for buff in self.buffs:
            base_regen, base_speed = buff.calculate(base_regen, base_speed)
        return base_regen, base_speed
