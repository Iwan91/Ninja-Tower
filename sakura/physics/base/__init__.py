from __future__ import division
from math import ceil
"""Basic in-game objects.
These objects fully represent given instances against the world of physics.
All objects here are oriented.

Resource IDs:

    b - map boundary
    a - actor
    s - shot
    p - platform
    o - obstacle

    g - geometry
    r - rectangle

Colors in actors and shots are properties such that actor can only interact with differently colored
shots
"""
from sakura.physics.base.primitives import Rectangle, Geometry
from sakura.physics.constants import GRAVITY_SUBINCREMENT, FRICTION

class MapBoundary(object):
    """If an actor intersects with map boundary, you MUST invoke jerk_actor on him.
    If a shot intersects with boundary, you must make it so it doesn't. This will vary according
    to chosen shot logic"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def intersects_a(self, other):
        return self.intersects_g(other.geometry, other.x+other.dx, other.y+other.dy)
    def intersects_s(self, other):
        return self.intersects_g(other.geometry, other.x+other.dx, other.y+other.dy)
    def intersects_r(self, other, xo, yo):
        otx = other.x1 + xo         # Oriented Top X
        if otx < 0: return True

        oty = other.y1 + yo
        if oty < 0:
            return True

        obx = other.x2 + xo
        if obx >= self.width: return True

        oby = other.y2 + yo
        if oby >= self.height: return True                
        
        return False

    def intersects_g(self, other, xo, yo):        
        return self.intersects_r(other.mbr, xo, yo)

    def jerk_actor(self, actor):
        other = actor.geometry.mbr

        otx = other.x1 + actor.x + actor.dx         # Oriented Top X
        if otx < 0:
            actor.x = -other.x1 + 1
            actor.dx = 0
            actor.h_braked = True
            actor.on_stop_horizontal_movement()

        oty = other.y1 + actor.y + actor.dy
        if oty < 0: 
            actor.y = -other.y1 + 1
            actor.dy = 0
            actor.v_braked = True
            # no roof here - you can't stick to map-top !

        obx = other.x2 + actor.x + actor.dx
        if obx >= self.width:
            actor.x = self.width - other.x2 - 1
            actor.dx = 0
            actor.h_braked = True
            actor.on_stop_horizontal_movement()

        oby = other.y2 + actor.y + actor.dy
        if oby >= self.height:
            # i do not understand now why these lines were here, but i'll keep them
            #if actor.dy < 0:
            #    actor.on_roof()
            #else:
            #    actor.on_touchdown()
            # instead of them a single actor.on_touchdown() has been inserted

            actor.v_braked = True
            actor.dy = 0

            actor.on_touchdown()

            # check if friction needs to be applied
            if actor.h_moving: return
            if abs(actor.dx) <= FRICTION:
                actor.dx = 0
                actor.on_stop_horizontal_movement()
            else:
                # Apply friction
                actor.dx += -abs(actor.dx)/actor.dx * FRICTION            

        assert not self.intersects_a(actor), 'Actor may not collide at the end of handler'


class Obstacle(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.rectangle = Rectangle(x1, y1, x2, y2)
        self.width = abs(self.x1-self.x2)
        self.height = abs(self.y1-self.y2)

    def intersects_r(self, rect, rx, ry):
        return self.rectangle.intersects_r(rect, 0, 0, rx, ry)

    def intersects_a(self, actor):
        return self.rectangle.intersects_g(actor.geometry, 0, 0, actor.x+actor.dx, actor.y+actor.dy)
    def intersects_s(self, shot):
        return self.rectangle.intersects_g(shot.geometry, 0, 0, shot.x+shot.dx, shot.y+shot.dy)
    def jerk_actor(self, actor):
        side_collided = min(((2, abs(actor.x + actor.geometry.mbr.x2 - self.x1)), 
                             (3, abs(actor.x + actor.geometry.mbr.x1 - self.x2)), 
                             (0, abs(actor.y + actor.geometry.mbr.y2 - self.y1)), 
                             (1, abs(actor.y + actor.geometry.mbr.y1 - self.y2))), key=lambda x: x[1])[0]

        if side_collided == 0:  # North
            actor.dy = 0
            actor.v_braked = True
            actor.on_touchdown()
            actor.y = self.y1 - actor.geometry.mbr.y2 - GRAVITY_SUBINCREMENT

            if not actor.h_moving:
                if abs(actor.dx) <= FRICTION:
                    actor.dx = 0
                    actor.on_stop_horizontal_movement()
                else:
                    # Apply friction
                    actor.dx += -abs(actor.dx)/actor.dx * FRICTION
        elif side_collided == 1:
            actor.dy = 0
            actor.v_braked = True
            actor.on_roof()
            actor.y = self.y2 - actor.geometry.mbr.y1 + GRAVITY_SUBINCREMENT
        elif side_collided == 2:
            actor.on_stop_horizontal_movement()
            actor.x = self.x1 - actor.geometry.mbr.x2 - GRAVITY_SUBINCREMENT
            actor.dx = 0
            actor.h_braked = True
            if actor.last_obstacle_collided != self:
                actor.v_braked = True
                actor.last_obstacle_collided = self
        elif side_collided == 3:
            actor.dx = 0
            actor.on_stop_horizontal_movement()
            actor.x = self.x2 - actor.geometry.mbr.x1 + GRAVITY_SUBINCREMENT
            actor.h_braked = True
            if actor.last_obstacle_collided != self:
                actor.v_braked = True
                actor.last_obstacle_collided = self

        assert not self.intersects_a(actor), 'Actor may not collide at the end of handler'

class Shot(object):
    def __init__(self, geometry_set, x, y, dx, dy, color, meta):
        """@param meta: meta is a supporting logic class. To be defined elsewhere and invoked
        by collision checking engine"""
        self.x = x
        self.color = color
        self.y = y
        self.dx = dx
        self.dy = dy
        self.meta = meta
        meta.shot = self
        self.animation_id = 0
        self.geometry_set = geometry_set
        self.geometry = geometry_set[0]

        self._last_sent_d = None, None
        self.packets_to_resend = 0

    def intersects_a(self, actor):
        return self.geometry.intersects_g(actor.geometry, self.x+self.dx, self.y+self.dy, actor.x+actor.dx, actor.y+actor.dy)

    def pick_geometry(self, i):
        self.geometry = self.geometry_set[i]
        self.animation_id = i

    def pick_geometry_b(self, i):
        """Same as pick_geometry, but expects base animation(ie. even).
        Direction will be automatically determined from the current animation_id"""
        self.pick_geometry(i + self.animation_id % 2)

class Actor(object):
    def __init__(self, geometry_set, x, y, color, meta):
        """@param geometry_set: dictionary(geometry id::int => Geometry)
        @param meta: meta is a supporting logic class. To be defined elsewhere and invoked
        by collision checking engine"""
        self._last_sent_d = 0, 0
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.meta = meta
        self.geometry_set = geometry_set
        self.geometry = self.geometry_set[0]
        self.animation_id = 0
        self.color = color

        self.v_braked = False       #: was forced to dy=0 on this turn
        self.h_braked = False       #: was forced to dx=0 on this turn
        self.is_on_roof = False     #: was forced to dy=0 on this turn due to collision with roof
        self.h_moving = True        #: actor innately wants to move [keys depressed]

        self.no_anchor = 0     # bool() it to get boolean value about the notion
                               # of having no anchor

        self.mass = 1       #: coefficient by which gravitic interactions are multiplied

        self.direction = 0  #: 0 - right, 1 - left

        self.last_obstacle_collided = None
        self.packets_to_resend = 0

    def autopick_geometry(self):
        """If is_on_roof, add 64
        Automatically apply direction.
        if dy!=0 pick 4
        If dx!=0, dy==0 pick 2
        If dx==dy==0 pick 0.

        calls pick_geometry"""
        i = 64 if self.is_on_roof else 0
        i += self.direction
        if self.dy != 0:
            return self.pick_geometry(i+4)
        elif self.dx != 0:
            return self.pick_geometry(i+2)
        else:
            return self.pick_geometry(i)


    def pick_geometry(self, i):
        self.geometry = self.geometry_set[i]
        self.animation_id = i

    def on_roof(self): # changes Geometry
        """Physics handling tells us that we have hit the roof (obstacle, map boundary)"""
        self.is_on_roof = True
        prev_g = self.geometry
        self.autopick_geometry()
        self.y += self.geometry.mbr.y1 - prev_g.mbr.y1

    def on_start_horizontal_movement(self):
        prev_g = self.geometry
        self.autopick_geometry()
        # correct y for geometry changes we need to correct for that.
        self.y -= self.geometry.mbr.y2 - prev_g.mbr.y2

    def on_stop_horizontal_movement(self):
        prev_g = self.geometry
        self.autopick_geometry()
        # correct y for geometry changes we need to correct for that.
        self.y -= self.geometry.mbr.y2 - prev_g.mbr.y2

    def on_touchdown(self): # changes Geometry
        """Physics handling tells us that we have hit the ground (platform, 
           obstacle, map boundary)"""
        prev_g = self.geometry
        self.autopick_geometry()
        # correct y for geometry changes we need to correct for that.
        self.y -= self.geometry.mbr.y2 - prev_g.mbr.y2


class Platform(object):
    """How to check actor collision against a platform:
        Check if actor has no anchor. If this is the case, there is no collision.
        If the actor does not intersect against the platform, there is no collision.
        If, in previous iteration, the actor was fully above the platform AND not intersecting
            Then there was a collision - you should invoke jerk_actor
            Else there is no collision
                You should probably increase anchor by one - folk lore says so
    """
    def __init__(self, startx, stopx, y):
        self.startx = startx
        self.stopx = stopx
        self.y = y

    def intersects_a(self, other):
        mr = Rectangle(self.startx, self.y, self.stopx, self.y)
        return mr.intersects_g(other.geometry, 0, 0, other.x+other.dx, other.y+other.dy)

    def jerk_actor(self, actor):
        actor.v_braked = True
        actor.dy = 0
        actor.on_touchdown()
        actor.y = self.y-actor.geometry.mbr.y2-GRAVITY_SUBINCREMENT

        # check if friction needs to be applied
        if actor.h_moving: return
        if abs(actor.dx) <= FRICTION:
            actor.dx = 0
        else:
            # Apply friction
            actor.dx += -abs(actor.dx)/actor.dx * FRICTION
