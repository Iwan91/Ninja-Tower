class SIDAllocator(object):
    def __init__(self):
        self.csid = -1

        self.allocated_sids = []

    def allocate_sid(self):
        while True:
            self.csid += 1
            if self.csid == 65536:
                self.csid = 0
            if self.csid not in self.allocated_sids:
                self.allocated_sids.append(self.csid)
                return self.csid

    def deallocate_sid(self, sid):
        self.allocated_sids.remove(sid)
