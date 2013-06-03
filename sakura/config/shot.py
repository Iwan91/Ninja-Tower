from sakura.instrumentation import log
from sakura.physics.base import Rectangle, Geometry
import sys
import ConfigParser
import os

def load_shot(sid):
    sid = str(sid)

    log('sakura.config.shot.load_shot: Compiling ', sid)

    # load geometry
    animations = {}     # or 'animations as geometry set'
    # Get all animations
    for anim_dir in [x for x in os.listdir(sys.argv[2]+'shot/'+sid) if x.startswith('anim')]:
        try:
            anim_id = int(anim_dir[4:].strip())
            cf = ConfigParser.ConfigParser()
            cf.read(sys.argv[2]+'shot/'+sid+'/'+anim_dir+'/hitbox.ini')

            sx, sy = cf.getint('synchroPoint', 'x'), cf.getint('synchroPoint', 'y')

            hitboxes = []
            for rectangle_id in xrange(0, cf.getint('main', 'rectangles')):
                section = 'hitBox%s' % (rectangle_id, )
                hitboxes.append(Rectangle(cf.getint(section, 'x1')-sx, cf.getint(section, 'y1')-sy,
                                          cf.getint(section, 'x2')-sx, cf.getint(section, 'y2')-sy))

            animations[anim_id] = Geometry(hitboxes)
        except:
            print 'sakura.config.shot.load_shot: Skipping %s' % (anim_dir, )

    # Perform upside-down animating
    for canims, geometry in animations.items():
      animations[canims | 64] = geometry.upside_down()

    d = {'animations':animations}

    return d
