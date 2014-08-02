# -*- coding: utf-8 -*-

#a really simple tracker
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
#useful utilities for parsing request headers
from urllib.parse import urlparse, parse_qs

info_hash_to_peers = {}

class peer:
    peer_id = ""
    ip_address = ""
    port = 0
    info_hashes = {}

class tracker(BaseHTTPRequestHandler):

    #dependancy injection for testing, NB could put this in the test code?
    def __init__(s, wfile, path, client_address, requestline, request_version):
        s.wfile = wfile
        s.path = path
        s.client_address = client_address
        s.requestline = requestline
        s.request_version = request_version
        
    def do_GET(s):
        #parse out the parameters of the request
        params = parse_qs(urlparse(s.path).query, keep_blank_values=1)

        #mandatory fields, should not return a result if these aren't provided.
        peer_id = params["peer_id"]
        info_hash = params["info_hash"]

        #use the address from the request, else check for ip_address in the parameters.
        ip_address, not_int = s.client_address
        if params.get("ip_address"):
            ip_address = params["ip_address"]

        #port is mandatory
        port = params["port"]

        #add this client as someone who has the file.
        #info_hash_to_peers[

        #get other peers for this info_hash and return them to the client.
        #other_peers = info_hash_to_peers.get("

        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        s.write("path=%s" % s.path)
        s.write("\nparams=%s" % params)
    def write(s, to_write):
        s.wfile.write(bytes(to_write, "UTF-8"))

#run the server if this was the main thing.
if __name__ == "__main__":
    httpd = HTTPServer((b"localhost", 8000), tracker)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


