class ReqTask(object):
    """
    Object that symbolizes an allocation request
    """
    def __init__(self, gugid, bpf_chunk):
        self.gugid = gugid
        self.bpf_chunk = bpf_chunk

        self.retry_count = 10

    def retry(self):
        """invoking this means that the task has failed, and should return a bool
        saying whether it should be rescheduled"""
        self.retry_count -= 1

        return self.retry_count > 0

