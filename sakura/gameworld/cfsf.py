"""Collisions for Scripts Facility"""
from sakura.physics.base.primitives import Rectangle

class CFSF(object):
    def __init__(self, gameworld):
        self.gameworld = gameworld
        self.physics = gameworld.physics

    def rect_boundary(self, rect, rx, ry):
        return self.physics.mapboundary.intersects_r(rect, rx, ry)

    def actor_boundary(self, actor):
        return self.physics.mapboundary.intersects_a(actor)

    def rect_obstacle(self, rect, rx, ry):
        for obstacle in self.gameworld.physics.obstacles:         
            if obstacle.intersects_r(rect, rx, ry):
                return True
        return False

    def actor_obstacle(self, actor):
        for obstacle in self.gameworld.physics.obstacles:         
            if obstacle.intersects_a(actor):
                return True
        return False

    def actor_rect_notteam(self, rect, notteam, rx=0, ry=0):
        """Return a list of actors that collide with rectangle, and are not in team notteam"""
        if not isinstance(rect, Rectangle):
            rct = Rectangle(*rect)
        else:
            rct = rect
        actors = []
        for actor in self.gameworld.physics.actors:
            if actor.meta.team == notteam: continue
            if actor.geometry.intersects_r(rct, actor.x, actor.y, rx, ry):
                actors.append(actor)
        return actors        

    def actor_point_notteam(self, point, notteam):
        """Return a list of actors that collide with point, and are not in team notteam"""
        actors = []
        for actor in self.physics.actors:
            if actor.meta.team == notteam: continue
            if actor.geometry.intersects_p(actor.x, actor.y, point[0], point[1]):
                actors.append(actor)
        return actors