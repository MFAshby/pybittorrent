#basic bittorrent client. Start off with single-file torrents, 
from bencode import bencode, bdecode
from struct import pack
from bitarray import bitarray
from hashlib import sha1

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
    write_message(b"", output_socket)      #empty message

def do_choke(output_socket):
    write_message(b"\x00", output_socket)  #message ID 0

def do_unchoke(output_socket):
    write_message(b"\x01", output_socket)  #message ID 1

def do_interested(output_socket):
    write_message(b"\x02", output_socket)  #message ID 2

def do_not_interested(output_socket):
    write_message(b"\x03", output_socket)  #message ID 3

def do_have(output_socket, piece_index):
    write_message(b"\x04" + int_bytes(piece_index), output_socket) #message ID 4

def do_bitfield(output_socket, pieces_bitarray):
    pieces_bitarray_bytearray = bytearray(pieces_bitarray.tobytes())
    pieces_bitarray_bytearray.insert(0, 5) #message ID 5
    write_message(pieces_bitarray_bytearray, output_socket)

def do_request(output_socket, piece_index, begin_index, length):
    write_message(b"\x06" #message ID 6
                + int_bytes(piece_index) 
                + int_bytes( begin_index)
                + int_bytes(length), output_socket) 

def do_piece(output_socket, piece_index, begin_index, block):
    write_message(b"\x07" #message ID 7
                + int_bytes(piece_index) 
                + int_bytes(begin_index)
                + block, output_socket)

def do_cancel(output_socket, piece_index, begin_index, length):
    write_message(b"\x08" #message ID 8
                + int_bytes(piece_index) 
                + int_bytes( begin_index)
                + int_bytes(length), output_socket) 

def write_message(message, output_socket):
    """Write length of message, then message"""
    output_socket.write(int_bytes(len(message)))
    output_socket.write(message)

def int_bytes(i):
    """pack an integer as 4 bytes big endian unsigned."""
    return pack(">I", i)

def check_piece(piece_data, piece_hash):
    piece_hash_test = sha1()
    piece_hash_test.update(piece_data)
    return piece_hash == piece_hash_test


def should_poll_tracker(peers, last_poll_time, current_time, interval):
    #poll regardless if we have no peers
    if not peers:
        return True
    #otherwise poll if the elapsed since last poll < 30s
    elapsed = current_time - last_poll_time
    return interval <= elapsed

def tracker_request_url(metainfo_file, peer_id, port, uploaded, downloaded, left, event):
    """Generate the URL to request from the tracker"""
    from urllib.parse import urlparse, urlencode, quote, urlunparse

    #create the info_hash from the info section of the metainfo file.
    info_string = bencode(metainfo_file["info"])
    s = sha1()
    s.update(bytes(info_string, "UTF-8"))
    info_hash = quote(s.digest())

    #generate the URL to request, take the existing announce URL from 
    #the metainfo_file
    scheme, netloc, path, params, query, fragment = urlparse(metainfo_file["announce"])

    #add query parameters
    query = urlencode({"info_hash": info_hash,
                       "peer_id": peer_id,
                       "port": port, 
                       "uploaded": uploaded, 
                       "downloaded": downloaded,
                       "left": left,
                       "event": event})

    #put the URL together and return it.
    return urlunparse((scheme, netloc, path, params, query, fragment))

def check_pieces(input_file, piece_length, pieces):
    have_pieces = bitarray()
    for piece_hash in chunks(pieces, 20):
        file_piece = input_file.read(piece_length)
        s = sha1()
        s.update(file_piece)
        have_pieces.append(s.digest() == piece_hash)
    return have_pieces

def chunks(string, number):
    for i in range(0, len(string), number):
        yield string[i: i+number]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Download using bittorrent')
    parser.add_argument('TORRENT', type=str, help='the .torrent file you want to download from')

    #parse the metainfo file
    args = parser.parse_args()
    metainfo_file = None
    with open(args.TORRENT, "r", encoding="iso-8859-15") as f:
        metainfo_file = bdecode(f.read())

    #work out how much of the file we already have downloaded
    info_dict = metainfo_file["info"]
    piece_length = info_dict["piece length"]
    pieces = info_dict["pieces"]
    with open(info_dict["name"], "rb") as output_file:
        have_pieces = check_pieces(output_file, piece_length, pieces)
    print("Got %d out of %d pieces" % (sum(have_pieces), len(have_pieces)))
        
    






