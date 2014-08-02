#basic bittorrent client. Start off with single-file torrents, 

#peers, by IP address
peers = {}

class Peer:
    am_choking = True
    am_interested = False
    peer_choking = True
    peer_interested = False

if __name__ == "__main__":
    
