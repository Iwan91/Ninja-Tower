from satella.threads import Monitor

class PlayerDatabaseTransaction(object):
    """
    Root class for all transactions against player database"""
    def __init__(self, playerdatabase):
        self.pdb = playerdatabase

    def run(self):
        """Override this with your own code"""
        raise NotImplementedError, 'abstract'

    def start(self, slave=False):
        """Organizes for transaction in run() to be run atomically.
        @param slave: set this to True if you invoke it from a 
        transaction so that lock is not reacquired.
        """
        self.pdb.transactions_counter.update()
        if not slave:
            with Monitor.acquire(self.pdb):
                return self.run()
        else:
            return self.run()