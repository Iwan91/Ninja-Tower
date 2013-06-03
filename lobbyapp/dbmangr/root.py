import MySQLdb

from satella.instrumentation.counters import PulseCounter
from satella.instrumentation import CounterCollection
from satella.db.pool import DatabaseDefinition, ConnectionPool

from lobbyapp.selectlayer.api import PDBHelperInterface as SelectLayerInterface
from lobbyapp.dbmangr.proxies import SelectLayerProxy, PlayerDBProxy

from lobbyapp.playerdb.api import PDBHelperInterface as PlayerDBInterface

class DatabaseManager(object):
    def __init__(self, host, username, password, dbname, rootcc, dbtype='mysql'):
        """@type rootcc: L{satella.instrumentation.CounterCollection}"""
        assert dbtype == 'mysql', 'I cannot support other databases!'

        dd = DatabaseDefinition(MySQLdb.connect, 
                                (MySQLdb.OperationalError, MySQLdb.InterfaceError), 
                                (host, username, password, dbname))

        self.cp = ConnectionPool(dd)

        # Set up instrumentation
        insmgr = CounterCollection('database')
        self.cursors_counter = PulseCounter('cursors', resolution=60, 
                                            units=u'cursors per minute',
                                            description='SQL cursors created')
        insmgr.add(self.cursors_counter)
        rootcc.add(insmgr)

    def query_interface(self, ifc):
        if ifc == SelectLayerInterface:
            return SelectLayerProxy(self)
        elif ifc == PlayerDBInterface:
            return PlayerDBProxy(self)
        else:
            raise ValueError, 'Unknown interface'

    def __call__(self):
        """
        Use as in:

            with database_manager() as cur:
                cur.execute('I CAN DO SQL')
        """
        self.cursors_counter.update()
        return self.cp.cursor()
