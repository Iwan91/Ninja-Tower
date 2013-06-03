from lshardmgr.main import MainClass

from time import sleep

from lshardmgr.signals import register_signals

if __name__ == '__main__':
    mc = MainClass()

    # register stuff
    register_signals(mc)


    while True:
        try:
            done_shards = mc.wait_for_shards()
        except:
            from satella.instrumentation.exctrack import Trackback
            print Trackback().pretty_print()
            break

        for shard in done_shards:
            pass

        with mc.monitor:
            if len(mc.shards) == mc.target_shard_number == 0:
                break

        sleep(5)
