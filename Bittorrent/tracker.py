from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib.parse import urlparse, parse_qsl
from collections import defaultdict
from uuid import uuid4
from random import sample

from bencode import bencode_file

info_hash_to_peers = defaultdict(dict)

class Peer(object):
    peer_id = ""
    ip_address = ""
    port = 0
    tracker_id = ""
    complete = 0

def handle_GET(handler, output_file):
    params = dict(parse_qsl(urlparse(handler.path).query, keep_blank_values=1))

    #mandatory fields
    info_hash = params["info_hash"]
    peer_id = params["peer_id"]        
    port = int(params["port"])

    #non-mandatory fields
    event = params.get("event", "")
    numwant = int(params.get("numwant", 50))

    #use the address from the request, else check for ip_address in the parameters.
    ip_address, x = handler.client_address
    if params.get("ip_address"):
        ip_address = params["ip_address"]

    peers_by_id = info_hash_to_peers[info_hash]

    #get a sample of peers to return to the client
    num_peers = min(numwant, len(peers_by_id))
    peers_sample = sample(list(peers_by_id.values()), num_peers)
    #turn them into the appropriate dictionary response
    peers_sample_list = [{"peer id":p.peer_id, "ip": p.ip_address, "port": p.port} for p in peers_sample]

    #add the client to peers list if they just started
    if event == "started":
        p = Peer()
        p.peer_id = peer_id
        p.ip_address = ip_address
        p.port = port
        p.tracker_id = str(uuid4())
        peers_by_id[peer_id] = p
    elif event == "complete":
        p = peers_by_id[peer_id]
        p.complete = 1

    #get the count of seeders/leechers (including ourselves?)
    total = 0
    complete = 0
    for peer_id, peer in peers_by_id.items():
        total += 1
        if peer.complete:
            complete += 1
    incomplete = total - complete

    #get the tracker ID we have generated for the client, if we have one
    tracker_id = peers_by_id.get(peer_id).tracker_id if peers_by_id.get(peer_id) else ""

    #send headers
    handler.send_response(200)
    handler.send_header("Content-type", "text/plain")
    handler.end_headers()

    #generate the final response
    response = {"interval": 30,
    "complete": complete,
    "incomplete": incomplete,
    "tracker id": tracker_id,
    "peers": peers_sample_list}
    bencode_file(output_file, response)

class Tracker(BaseHTTPRequestHandler):
    def do_GET(self):
        handle_GET(self, self.wfile)

if __name__ == "__main__":
    #todo take arguments for where to bind to.
    httpd = HTTPServer((b"localhost", 8000), Tracker)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


