import os
from copy import copy
import json
import struct
import subprocess
from satella.threads import BaseThread
from socket import AF_INET, SOCK_STREAM, socket

class SpawnObject(object):
    def __init__(self, mc, bpf_chunk, gugid):
        self.mc = mc
        self.gugid = gugid
        self.tcp_port, self.udp_port = mc.allocate_ports()

        self.source_bpf = copy(bpf_chunk)

        # Prepare BPF file
        bpf_chunk['tcp_port'] = self.tcp_port
        bpf_chunk['udp_port'] = self.udp_port
        bpf_chunk['tcp_interface'] = mc.outside_visible_interface
        bpf_chunk['udp_interface'] = mc.outside_visible_interface
        bpf_chunk['version'] = 'alpha'

        self.bpf_guid = mc.getguid()
        self.out_guid = mc.getguid()
        self.stdout_guid = mc.getguid()

        # Store the BPF file
        bpff = open(mc.tmp_root+str(self.bpf_guid), 'wb')
        json.dump(bpf_chunk, bpff)
        bpff.close()

    def poll(self):
        """Return True if finished successfully.
        Also reads retval if it can"""
        self.rc = self.popen.poll()
        if self.rc == None: return False

        self.stdout.close()

        if self.rc < 0:
            print 'lshardmgr: Shard %s ABEND=%s' % (self.pid, -self.rc)
        else:
            print 'lshardmgr: Shard %s CC=%s' % (self.pid, self.rc)

        # finished, attempt to get the return
        try:
            rtv = open(self.mc.tmp_root+str(self.out_guid), 'rb')
            self.return_data = json.load(rtv)
            rtv.close()
        except:
            self.return_data = None

        return True

    def start(self):
        self.stdout = open(self.mc.tmp_root+str(self.stdout_guid), 'wb')

        # construct the popen stuff
        npp = []
        for arg in self.mc.sakura_popen:
            if arg == '%BPF%':
                npp.append(self.mc.tmp_root+str(self.bpf_guid))
            elif arg == '%OUT%':
                npp.append(self.mc.tmp_root+str(self.out_guid))
            else:
                npp.append(arg)

        self.popen = subprocess.Popen(npp, stdin=open('/dev/null'), stdout=self.stdout, stderr=subprocess.STDOUT)
        self.pid = self.popen.pid
        print 'lshardmgr: Shard started, PID=%s, PORT=%s' % (self.pid, self.tcp_port)

    def free(self):
        # Return ports
        self.mc.release_port(self.tcp_port)

        # Remove files
        os.unlink(self.mc.tmp_root+str(self.bpf_guid))

        try:
            os.unlink(self.mc.tmp_root+str(self.stdout_guid))
        except:
            pass        

        try:
            os.unlink(self.mc.tmp_root+str(self.out_guid))
        except:
            pass


        class SendToServerThread(BaseThread):
            def __init__(self, pts, mc):
                BaseThread.__init__(self)
                self.pts = pts
                self.mc = mc

            def run(self):
                dpak = json.dumps(self.pts)

                sock = socket(AF_INET, SOCK_STREAM)
                sock.settimeout(30)
                sock.connect(self.mc.statistics_interface)
                sock.send(struct.pack('>L', len(dpak))+dpak)
                sock.close()

        rd = self.return_data

        try:
            # if it's None then KeyError will be thrown at any time
            if rd['reason'] == 'nobody_logged_in':
                SendToServerThread({
                        'gugid': self.gugid,
                        'winner': None,
                        'status': 1
                    }, self.mc).start()
            else:
                SendToServerThread({
                        'gugid': self.gugid,
                        'winner': rd.winner,
                        'status': 1
                    }, self.mc).start()
        except (KeyError, TypeError, AttributeError):
            SendToServerThread({
                    'gugid': self.gugid,
                    'winner': None,
                    'status': 0
                }, self.mc).start()            