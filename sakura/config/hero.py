from sakura.instrumentation import log
from sakura.physics.base import Rectangle, Geometry
import sys
import ConfigParser
import os

def load_hero(charname):

    log('sakura.config.hero.load_hero: Compiling ', charname)

    cf = ConfigParser.ConfigParser()
    cf.read(sys.argv[2]+'heroes/'+charname+'/infoHero.ini')    
    cf.read(sys.argv[2]+'heroes/'+charname+'/infoSkills.ini')    

    related_shots_list = []
    for rsc in cf.get('general', 'related_shots').split(' '):
      try:
        int(rsc)
      except:
        pass
      else:
        related_shots_list.append(int(rsc))

    d = {'name': cf.get('general', 'name'),
         'speed': cf.getfloat('general', 'speed'),
         'jump': cf.getfloat('general', 'jump'),
         'mass': cf.getfloat('general', 'mass'),
         'related_shots': related_shots_list,
         'hp': cf.getfloat('general', 'hp'),
         'regen': cf.getfloat('general', 'regen')}

    def import_skill(skillname):
        return __import__('sakura.scripting.library.skill', globals(), locals(), [skillname]).__dict__[skillname].Skill

    d['skilltab'] = [None, None, None, None, None]
    for keyid, skillkey in [(2, 'shift'), (0, 'q'), (1, 'e'), (3, 'lpm'), (4, 'ppm')]:
      secname = 'vkey_'+skillkey
      args = []
      # Fetch arguments
      for i in xrange(1, 1000):
        try:
          arg = cf.get(secname, 'arg%s' % (i, ))
        except:
          break
        else:
          args.append(arg)
      # Fetch cooldown
      try:
        cooldown = float(cf.get(secname, 'cooldown'))
      except:
        d['skilltab'][keyid] = 0, lambda invoker: import_skill('noop')(invoker)
        continue
      # Fetch name
      try:
        skillname = cf.get(secname, 'name')
      except:
        d['skilltab'][keyid] = 0, lambda invoker: import_skill('noop')(invoker)

      skillobject = import_skill(skillname)        

      def closeover(skillobject, args):
        def skill_closure(invoker):
          return skillobject(invoker, *args)
        return skill_closure

      # Add the cooldown and generating closure
      d['skilltab'][keyid] = cooldown, closeover(skillobject, args)

    del cf

    animations = {}     # or 'animations as geometry set'
    # Get all animations
    for anim_dir in [x for x in os.listdir(sys.argv[2]+'heroes/'+charname) if x.startswith('anim')]:
        try:
          anim_id = int(anim_dir[4:].strip())
          cf = ConfigParser.ConfigParser()
          cf.read(sys.argv[2]+'heroes/'+charname+'/'+anim_dir+'/hitbox.ini')

          sx, sy = cf.getint('synchroPoint', 'x'), cf.getint('synchroPoint', 'y')

          hitboxes = []
          for rectangle_id in xrange(0, cf.getint('main', 'rectangles')):
              section = 'hitBox%s' % (rectangle_id, )
              hitboxes.append(Rectangle(cf.getint(section, 'x1')-sx, cf.getint(section, 'y1')-sy,
                                        cf.getint(section, 'x2')-sx, cf.getint(section, 'y2')-sy))

          animations[anim_id] = Geometry(hitboxes)
          animations[anim_id+64] = Geometry(hitboxes).upside_down()
        except:
          print 'sakura.config.hero.load_hero: Skipping %s' % (anim_dir, )

    d['animations'] = animations

    return d