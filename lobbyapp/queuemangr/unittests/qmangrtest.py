import unittest

from satella.instrumentation import CounterCollection

from lobbyapp.queuemangr import QueueManager

class QueueManagerTest(unittest.TestCase):
    def test_queuemanager(self):
        q = {'2vs2': {
                    'players_per_match': 4
                }
            }

        rootcc = CounterCollection('test')

        q = QueueManager(q, rootcc)

        self.assertEquals(q.has_queue('2vs2'), True)
        self.assertEquals(q.has_queue('dogbert'), False)

        q.queues['2vs2'].enqueue(2)
        self.assertRaises(ValueError, q.queues['2vs2'].enqueue, 2)