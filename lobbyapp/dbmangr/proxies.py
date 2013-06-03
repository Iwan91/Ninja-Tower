"""
Army of proxy objects to cater for different layers
"""

from lobbyapp.selectlayer.api import PDBHelperInterface as SelectLayerPrototype
from lobbyapp.playerdb.api import PDBHelperInterface as PlayerDBPrototype

class PlayerDBProxy(PlayerDBPrototype):
    def __init__(self, dbmangr):
        self.dbmangr = dbmangr

    def get_login_for_pid(self, pid):
        """Given pid, return the login. Throw IndexError on not found"""
        with self.dbmangr() as cur:
            cur.execute('SELECT member_name FROM smf_members WHERE id_member=%s', (pid, ))
            k = cur.fetchone()
            if k == None:
                raise IndexError, 'no such player'
            else:
                return k[0]

    def get_password_for_pid(self, pid):
        """Given pid, return the password in hashed form. Throw IndexError on not found"""
        with self.dbmangr() as cur:
            cur.execute('SELECT passwd FROM smf_members WHERE id_member=%s', (pid, ))
            k = cur.fetchone()
            if k == None:
                raise IndexError, 'no such player'
            else:
                return k[0]

    def get_available_heroes(self, pid):
        """Return a list of available hero identifiers"""
        return ['Ayatsuri']
        # commented out until more heroes are available
        with self.dbmangr() as cur:
            cur.execute('SELECT heroes FROM players_heroes WHERE pid=%s', (pid, ))
            k = cur.fetchone()
            if k == None:
                # entry does not exist
                return []
            else:
                return k[0].split(',')

class SelectLayerProxy(SelectLayerPrototype):
    def __init__(self, dbmangr):
        self.dbmangr = dbmangr

    def authenticate(self, login, password):
        """
        @param login: User login
        @type login: str

        @param password: User password
        @type password: str

        @return: (pid, 0) if credentials are OK
            (-1, None) if credentials are invalid
            (-2, datetime.datetime x) if banned until
        """
        with self.dbmangr() as cur:
            cur.execute('SELECT id_member FROM smf_members WHERE (member_name=%s) AND (passwd=%s)', (login, password))
            k = cur.fetchone()
            if k == None:
                return (-1, None)    # credentials invalid: login
            else:
                return (k[0], 0)    # success
