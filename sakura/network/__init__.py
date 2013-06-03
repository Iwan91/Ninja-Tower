from sakura.instrumentation import log
from sakura import config
from sakura.network.sequencer import Sequencer
from sakura.network.select_loop import SelectLoop
import socket

def init_sockets():
    log('sakura.network.init_sockets: Initializing network sockets')
    config.registry['tcp_socket'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    config.registry['tcp_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    config.registry['tcp_socket'].bind(config.registry['tcp_bind'])

    config.registry['udp_socket'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    config.registry['udp_socket'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    config.registry['udp_socket'].bind(config.registry['udp_bind'])

def init_sequencer():
    log('sakura.network.init_sequencer: Initializing sequencer')
    config.registry['_runtime']['sequencer'] = Sequencer()

def init_network():
    log('sakura.network.init_sequencer: Firing up the network')
    config.registry['_runtime']['select_loop_thread'] = SelectLoop()
    config.registry['_runtime']['select_loop_thread'].start()

