"""
The job of select layer:


    - do the network interfacing with users
    - send information about actions and events to upper layer,
        whilst abstracting away network interfaces, timeouts,
        errors and so on

    See MANIFEST for interlinking details
"""
from lobbyapp.selectlayer.selectlayer import PlayersHandlingLayer