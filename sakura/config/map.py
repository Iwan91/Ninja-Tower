import sys
import ConfigParser
from sakura.physics.base import Platform, Obstacle, MapBoundary
from sakura.instrumentation import log

def load_map(mapname):
    log('sakura.config.map.load_map: Compiling ', mapname)
    cf = ConfigParser.ConfigParser()
    cf.read(sys.argv[2]+'maps/'+mapname+'/info.ini')

    # Read basic info
    d = {'mapname': cf.get('Main', 'MapName'),
         'width':   cf.getint('Main', 'Width'),
         'height':  cf.getint('Main', 'Height'),
         'map_boundary': MapBoundary(cf.getint('Main', 'Width'), cf.getint('Main', 'Height'))}

    # Read platforms
    platforms = []
    for platform_id in xrange(0, cf.getint('Main', 'Platforms')):

        section = 'Platform%s' % (platform_id, )
        x = cf.getint(section, 'X')
        width = cf.getint(section, 'Width')

        platforms.append(Platform(x, x+width, cf.getint(section, 'Y')))
    d['platforms'] = platforms

    # Read obstacles
    obstacles = []
    for obstacle_id in xrange(0, cf.getint('Main', 'Obstacles')):

        section = 'Obstacle%s' % (obstacle_id, )

        obstacles.append(Obstacle(cf.getint(section, 'X1'), cf.getint(section, 'Y1'),
                                  cf.getint(section, 'X2'), cf.getint(section, 'Y2')))
    d['obstacles'] = sorted(obstacles, key=lambda x: -x.y1)

    # Read spawnpoints
    spawnpoints = []
    for spawnpoint_id in xrange(0, 2):

        section = 'Team%s' % (spawnpoint_id, )

        spawnpoints.append((cf.getint(section, 'SpawnX'), cf.getint(section, 'SpawnY')))
    d['spawnpoints'] = spawnpoints

    return d