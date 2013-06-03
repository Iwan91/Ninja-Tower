from threading import Lock

try:
    lck
except:
    lck = Lock()

def log(*args, **kwargs):
    with lck:
        print ''.join(map(str,args))