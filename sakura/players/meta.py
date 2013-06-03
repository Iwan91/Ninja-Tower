class MetaActorSupportingClass(object):
    """Abstract class to be used as interface"""
    def on_shot(self, shot):
        """On collision with shots"""
        pass

    def on_obstacle(self, obstacle):
        """On collision with obstacle"""
        pass

    def wants_removal(self):
        return False

    def on_damage(self, damage):
        pass

class MetaShotSupportingClass(object):
    """
    Semi-abstract class to be used as interface
    Will have a public attribute 'sid' - GameWorld will create it
    Must have a class/public attribute 'shot_type' - ID of the shot type
    Will have a attribute 'shot'  - shot initializer will ensue this
    """
    def on_tick(self, gameworld):
        """Called on each iteration. Shot is this shot"""
        if self.shot.dx >= 0:
            self.shot.pick_geometry(0)
        else:
            self.shot.pick_geometry(1)

    def wants_removal(self):
        return False

    def on_actor(self, actor):
        """On collision with actor"""

    def on_obstacle(self, obstacle):
        """On collision with obstacle"""

    def on_boundary(self, mapboundary):
        """On collision with map boundary"""
