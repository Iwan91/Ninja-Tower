from signal import signal, SIGUSR1, SIGUSR2

def on_SIGUSR(signum, frame, mc):
    if signum == SIGUSR1:
        mc.target_shard_number -= 1
        print 'lshardmgr: Received SIGUSR1, shards lowered to %s' % (mc.target_shard_number, )
    elif signum == SIGUSR2:
        mc.target_shard_number += 1
        print 'lshardmgr: Received SIGUSR1, shards upped to %s' % (mc.target_shard_number, )

def register_signals(mc):
    signal(SIGUSR1, lambda signum, frame: on_SIGUSR(signum, frame, mc))
    signal(SIGUSR2, lambda signum, frame: on_SIGUSR(signum, frame, mc))
