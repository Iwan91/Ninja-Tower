class PDBHelperInterface(object):
    """
    PDB helper passed to playerdb.PlayerDatabase must conform to 
    this interface
    """

    def get_match_id_for_player(self, pid):
        """Returns MID for given player or None
        if there's no match"""
        raise NotImplementedError, 'abstract method'

    def get_login_for_pid(self, pid):
        """Given pid, return the login. Throw IndexError on not found"""
        raise NotImplementedError, 'abstract method'
        
    def get_available_heroes(self, pid):
        """Return a list of available hero identifiers"""
        raise NotImplementedError, 'abstract method'

    def get_password_for_pid(self, pid):
        """Given pid, return the password. Throw IndexError on not found"""
        raise NotImplementedError, 'abstract method'