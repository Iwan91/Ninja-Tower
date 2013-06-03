from sakura.physics.constants import GRAVITY_INCREMENT, GRAVITY_SUBINCREMENT

class Simulation(object):
    """Simulation is an agent of physics in the world of the game"""
    def __init__(self, mapboundary, platforms, obstacles):
        self.mapboundary = mapboundary
        self.platforms = platforms
        self.obstacles = obstacles
        self.actors = []
        self.shots = []

    def new_iteration(self):
        """On end of current iteration"""
        for actor in self.actors:
            actor.v_braked = False
            actor.h_braked = False

    def iteration(self):
        """Returns tuple of (sequence of Removed Shots, )"""
        # Step 1: Remove those who want to
        shots = []
        removed_shots = []
        for shot in self.shots:
            if shot.meta.wants_removal():
                removed_shots.append(shot)
            else:
                shots.append(shot)
        self.shots = shots

        self.actors = [actor for actor in self.actors if not actor.meta.wants_removal()]

        # Step 2: Apply gravity to actors
        for actor in self.actors:
            actor.meta.on_apply_gravity(GRAVITY_INCREMENT)

        # Step 3: Resolve collisions

            # Actor collides with ...
        for actor in self.actors:           
            for obstacle in self.obstacles:           # obstacles
                if obstacle.intersects_a(actor):
                    obstacle.jerk_actor(actor)
                    actor.meta.on_obstacle(obstacle)
            for obstacle in self.obstacles:           # obstacles
                if obstacle.intersects_a(actor):
                    obstacle.jerk_actor(actor)
                    actor.meta.on_obstacle(obstacle)

            for shot in self.shots[:]:                   # shots
                if shot.color == actor.color: continue
                if shot.intersects_a(actor):
                    actor.meta.on_shot(shot)
                    shot.meta.on_actor(actor)

            if self.mapboundary.intersects_a(actor):  # map boundary
                self.mapboundary.jerk_actor(actor)

            if actor.no_anchor: continue
            if actor.dy < 0: continue

            for platform in self.platforms:        # platforms
                if platform.intersects_a(actor):
                    if actor.geometry.mbr.y2+actor.y-actor.dy-GRAVITY_INCREMENT <= platform.y:
                        # There is a collision
                        platform.jerk_actor(actor)

            # Shot collides with ...
        for shot in self.shots[:]:      # self.shots is R/W for now
            for obstacle in self.obstacles:
                if obstacle.intersects_s(shot):
                    shot.meta.on_obstacle(obstacle)
            if self.mapboundary.intersects_s(shot):
                shot.meta.on_boundary(self.mapboundary)
            
        # Step 4: Move peoples
        for actor in self.actors:
            actor.x += actor.dx
            actor.y += actor.dy
            if actor.x < 0: actor.x = 0
            if actor.y < 0: actor.y = 0
        for shot in self.shots:
            shot.x += shot.dx
            shot.y += shot.dy
            if shot.x < 0: shot.x = 0
            if shot.y < 0: shot.y = 0

        # Step 5: Return
        return (removed_shots, )
