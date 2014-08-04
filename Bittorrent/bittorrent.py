#basic bittorrent client. Start off with single-file torrents, 
from bencode import bdecode

#index of pieces and whether we have them. (have_pieces[0] == 1) 
#if we have the first piece. have_pieces[123] == 0 if we don't 
#have the 124th piece
have_pieces = []

def do_handshake(output_socket, info_hash, peer_id):
    output_socket.write(b"\x13")
    output_socket.write(bytes("BitTorrent protocol", "UTF-8"))
    output_socket.write(b'\x00'*8)
    output_socket.write(bytes(info_hash, "UTF-8"))
    output_socket.write(bytes(peer_id, "UTF-8"))

def get_peer_id():
    import random
    import string
    max_char = string.ascii_uppercase + string.digits
    return "-PY0001-" + ''.join(random.choice(max_char) for _ in range(12))
    
def do_keep_alive(output_socket):
    output_socket.write(b"\x00")

def do_choke(output_socket):
    output_socket.write(b"\x01\x00")

def do_unchoke(output_socket):
    output_socket.write(b"\x01\x01")

def do_interested(output_socket):
    output_socket.write(b"\x01\x02")

def do_not_interested(output_socket):
    output_socket.write(b"\x01\x03")

def do_have(output_socket, piece_index):
    output_socket.write(b"\x05\x04")
