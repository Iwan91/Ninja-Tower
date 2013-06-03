import socket, ssl, struct, json, hashlib

def pkjson(data):
    x = json.dumps(data)
    return struct.pack('>L', len(x))+x

def rdjson(sck):
    ln, = struct.unpack('>L', str(sck.read(4)))
    return json.loads(str(sck.read(ln)))


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket = ssl.wrap_socket(socket)
socket.connect(('henrietta.com.pl', 4001))

socket.send(pkjson({'login': 'henrietta', 'password': hashlib.sha1('henriettabohrok2405').hexdigest()}))
resp = rdjson(socket)
print resp

if resp['status'] != 'ok': 
    print 'Failed to login, SYMPTOM=%s' % resp
else:
    print 'LOGIN OK'

socket.send(pkjson({'operation': 'server_statistics'}))
print rdjson(socket)

import sys
sys.exit()



socket.send(pkjson({'operation': 'enqueue', 'gametype': '1vs1'}))
print rdjson(socket)      # receive OK
print rdjson(socket)      # receive match found
print 'Match found'
socket.send(pkjson({'operation': 'match_pick', 'hero':'Temari'}))
rdjson(socket)      # receive OK
rdjson(socket)      # receive hero picked
print 'Hero picked'
#socket.send(pkjson({'operation': 'hero_lock_in'}))
#rdjson(socket)
#rdjson(socket)
#print 'Hero locked in'

# match should get started now
print rdjson(socket)

