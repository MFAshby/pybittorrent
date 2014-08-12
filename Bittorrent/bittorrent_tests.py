from unittest import TestCase, main
from io import BytesIO
import bittorrent
from bitarray import bitarray
from struct import unpack

def do_test_fn_return_output_socket(function, *args):
    output_socket = BytesIO()
    function(output_socket, *args)
    output_socket.seek(0)
    return output_socket

def read_int(socket):
    i, = unpack(">I", socket.read(4))
    return i

class BittorrentTest(TestCase):
    def test_handshake(self): 
        info_hash = "info4567890123456789"
        peer_id = "peer4567890123456789"
        output_socket = do_test_fn_return_output_socket(bittorrent.do_handshake, info_hash, peer_id)
        self.assertTrue(output_socket.read(1)[0] == 19) #first byte is protocol string length, should be 19
        self.assertTrue(output_socket.read(19).decode("UTF-8") == "BitTorrent protocol") #next 19 bytes are the protocol string
        self.assertTrue(output_socket.read(8) == b'\x00'*8) #8 empty bytes for protocol extensions
        self.assertTrue(output_socket.read(20).decode("UTF-8") == info_hash) #20 byte info hash
        self.assertTrue(output_socket.read(20).decode("UTF-8") == peer_id) #20 byte peer id

    def test_peer_id(self):
        peer_id = bittorrent.get_peer_id()
        self.assertTrue(len(peer_id) == 20)
        self.assertTrue(peer_id.startswith("-PY0001-"))
        #subsequent call returns a different peer_id
        peer_id_2 = bittorrent.get_peer_id()
        self.assertTrue(len(peer_id_2) == 20)
        self.assertTrue(peer_id_2.startswith("-PY0001-"))
        self.assertTrue(peer_id != peer_id_2)

    def test_keep_alive(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_keep_alive)
        #4 byte unsigned int, representing 0 length
        self.assertTrue(read_int(output_socket) == 0)

    def test_choke(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_choke)
        self.assertTrue(read_int(output_socket) == 1)  #length 1
        self.assertTrue(output_socket.read(1)[0] == 0) #message ID 0

    def test_unchoke(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_unchoke)
        self.assertTrue(read_int(output_socket) == 1)  #length 1
        self.assertTrue(output_socket.read(1)[0] == 1) #message ID 1

    def test_interested(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_interested)
        self.assertTrue(read_int(output_socket) == 1)  #length 1
        self.assertTrue(output_socket.read(1)[0] == 2) #message ID 2

    def test_not_interested(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_not_interested)
        self.assertTrue(read_int(output_socket) == 1)  #length 1
        self.assertTrue(output_socket.read(1)[0] == 3) #message ID 3

    def test_have(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_have, 1)
        self.assertTrue(read_int(output_socket) == 5)  #length 5
        self.assertTrue(output_socket.read(1)[0] == 4) #message ID 4
        self.assertTrue(read_int(output_socket) == 1)  #int piece index, 1

        output_socket = do_test_fn_return_output_socket(bittorrent.do_have, 9999)
        self.assertTrue(read_int(output_socket) == 5)  #length 5
        self.assertTrue(output_socket.read(1)[0] == 4) #message ID 4
        self.assertTrue(read_int(output_socket) == 9999)  #int piece index, 9999

    def test_bitfield(self):
        pieces_bitarray = bitarray("00000000000001")
        output_socket = do_test_fn_return_output_socket(bittorrent.do_bitfield, pieces_bitarray)
        self.assertTrue(read_int(output_socket) == 3)  #length 3
        self.assertTrue(output_socket.read(1)[0] == 5) #message ID 5
        self.assertTrue(output_socket.read() == pieces_bitarray.tobytes()) #14 bits with the last bit set, padded to 2 bytes with 0s.

    def test_request(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_request, 15, 100, 2^14)
        self.assertTrue(read_int(output_socket) == 13)   #length 13 
        self.assertTrue(output_socket.read(1)[0] == 6)   #message ID 6        
        self.assertTrue(read_int(output_socket) == 15)   #piece index (0 in this case)
        self.assertTrue(read_int(output_socket) == 100)  #begin index (0 in this case)
        self.assertTrue(read_int(output_socket) == 2^14) #length (2^14 in this case)

    def test_piece(self):
        test_block = b"TESTINGBLOCKOFDATA"
        output_socket = do_test_fn_return_output_socket(bittorrent.do_piece, 0, 100, test_block)
        self.assertTrue(read_int(output_socket) == 9+len(test_block))
        self.assertTrue(output_socket.read(1)[0] == 7)  #message ID 7
        self.assertTrue(read_int(output_socket) == 0)   #piece index
        self.assertTrue(read_int(output_socket) == 100) #begin 
        self.assertTrue(output_socket.read() == test_block)

    def test_cancel(self):
        output_socket = do_test_fn_return_output_socket(bittorrent.do_cancel, 15, 100, 2^14)
        self.assertTrue(read_int(output_socket) == 13)   #length 13 
        self.assertTrue(output_socket.read(1)[0] == 8)   #message ID 8
        self.assertTrue(read_int(output_socket) == 15)   #piece index (0 in this case)
        self.assertTrue(read_int(output_socket) == 100)  #begin index (0 in this case)
        self.assertTrue(read_int(output_socket) == 2^14) #length (2^14 in this case)

    def test_piece_check(self):
        from hashlib import sha1
        self.assertFalse(bittorrent.check_piece(b"TEST_PIECE_DATA", b"01234567890123456789"))
        piece_hash = sha1()
        piece_hash.update(b"TEST_PIECE_DATA")
        self.assertFalse(bittorrent.check_piece(b"TEST_PIECE_DATA", piece_hash))

    def test_should_poll_tracker(self):
        peers = []                 # poll if no peers. 
        last_poll_time = 0
        current_time = 10
        interval = 30
        self.assertTrue(bittorrent.should_poll_tracker(peers, last_poll_time, current_time, interval))

        peers = ["Here is a peer"] # poll if time over interval time. 
        last_poll_time = 0
        current_time = 40
        interval = 30
        self.assertTrue(bittorrent.should_poll_tracker(peers, last_poll_time, current_time, interval))

        peers = ["Here is a peer"] # don't poll if peers, and under time
        last_poll_time = 0
        current_time = 10
        interval = 30
        self.assertFalse(bittorrent.should_poll_tracker(peers, last_poll_time, current_time, interval))

    def test_tracker_request(self):
        from urllib.parse import parse_qsl, urlparse
        from hashlib import sha1
        from urllib.parse import quote
        from bencode import bencode

        #generate parameters
        info_dict = {"piece length": 512000, 
                     "pieces": "0123456789012345678901234567890123456789", 
                     "name":"myfile.txt",
                     "length": 1024000}
        s = sha1()
        s.update(bytes(bencode(info_dict), "UTF-8"))
        test_info_hash = quote(s.digest())

        metainfo_file = {"info": info_dict, 
                         "announce": "http://localhost:8000"}

        peer_id = "01234567890123456789"
        port = 8001
        uploaded = 512000
        downloaded = 511999
        left = 1
        event = "started"

        #generate the request URL
        request_url = bittorrent.tracker_request_url(metainfo_file, peer_id, port, uploaded, downloaded, left, event)

        #check the request URL can be parsed as a URL...
        request_dict = dict(parse_qsl(urlparse(request_url).query, keep_blank_values=1))

        #check the request contains the appropriate info. 
        self.assertTrue(request_dict["info_hash"] == test_info_hash)
        self.assertTrue(request_dict["peer_id"] == peer_id)
        self.assertTrue(request_dict["port"] == "8001")
        self.assertTrue(request_dict["uploaded"] == "512000")
        self.assertTrue(request_dict["downloaded"] == "511999")
        self.assertTrue(request_dict["left"] == "1")
        self.assertTrue(request_dict["event"] == "started")

    def test_check_pieces(self):
        from hashlib import sha1
        input_file = BytesIO(b"0123456789012345678901234567890123456789012345678901234567890123456789")
        piece_length = 20

        #generate pieces as if we had every piece of the file. 
        pieces = b""
        file_piece = input_file.read(piece_length)
        while file_piece:
            s = sha1()
            s.update(file_piece)
            pieces += s.digest()
            file_piece = input_file.read(piece_length)
        input_file.seek(0) #seek the file back to 0...
        have_pieces = bittorrent.check_pieces(input_file, piece_length, pieces)
        self.assertTrue(have_pieces == bitarray("1111"))

        #same thing again, but change one of the piece hashes
        input_file.seek(0) #seek the file back to 0...
        pieces = pieces[0:20] + b"00000000000000000000" + pieces[40:]
        have_pieces = bittorrent.check_pieces(input_file, piece_length, pieces)
        #should now be "missing" the second piece of the file. 
        self.assertTrue(have_pieces == bitarray("1011"))

    def test_chunks(self):
        index = 0
        for chunk in bittorrent.chunks("TESTING", 2):
            if index == 0:
                self.assertTrue(chunk == "TE")
            elif index == 2:
                self.assertTrue(chunk == "ST")
            elif index == 4:
                self.assertTrue(chunk == "IN")
            elif index == 6:
                self.assertTrue(chunk == "G")
            self.assertTrue(index <= 6)
            index = index+2

if __name__ == "__main__":
    main()


