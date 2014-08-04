from unittest import TestCase, main
from io import BytesIO
import bittorrent


class BittorrentTest(TestCase):
    def test_handshake(self): 
        info_hash = "info4567890123456789"
        peer_id = "peer4567890123456789"
        output = self.do_test_fn_return_output(bittorrent.do_handshake, info_hash, peer_id)
        #58 bytes total output
        self.assertTrue(len(output) == 68)
        #first byte is protocol string length, should be 19
        self.assertTrue(output[0] == 19)
        #next 19 bytes are the protocol string
        self.assertTrue(output[1:20].decode("UTF-8") == "BitTorrent protocol")
        #8 empty bytes
        self.assertTrue(output[20:28] == b'\x00'*8)
        #20 byte info hash
        self.assertTrue(output[28:48].decode("UTF-8") == info_hash)
        #20 byte peer id
        self.assertTrue(output[48:68].decode("UTF-8") == peer_id)

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
        output = self.do_test_fn_return_output(bittorrent.do_keep_alive)
        self.assertTrue(len(output) == 1)
        self.assertTrue(output[0] == 0)

    def test_choke(self):
        output = self.do_test_fn_return_output(bittorrent.do_choke)
        self.assertTrue(len(output) == 2)
        self.assertTrue(output[0] == 1) #length 1
        self.assertTrue(output[1] == 0) #message ID 0

    def test_unchoke(self):
        output = self.do_test_fn_return_output(bittorrent.do_unchoke)
        self.assertTrue(len(output) == 2)
        self.assertTrue(output[0] == 1) #length 1
        self.assertTrue(output[1] == 1) #message ID 1

    def test_interested(self):
        output = self.do_test_fn_return_output(bittorrent.do_interested)
        self.assertTrue(len(output) == 2)
        self.assertTrue(output[0] == 1) #length 1
        self.assertTrue(output[1] == 2) #message ID 2

    def test_not_interested(self):
        output = self.do_test_fn_return_output(bittorrent.do_not_interested)
        self.assertTrue(len(output) == 2)
        self.assertTrue(output[0] == 1) #length 1
        self.assertTrue(output[1] == 3) #message ID 3

    def test_have(self):
        output = self.do_test_fn_return_output(bittorrent.do_have, 1)
        self.assertTrue(len(output) == 2)
        self.assertTrue(output[0] == 5) #length 5
        self.assertTrue(output[1] == 4) #message ID 4
        self.assertTrue(output[1:4] == b"\x00\x00\x00\x01")

    def do_test_fn_return_output(self, function, *args):
        output_socket = BytesIO()
        function(output_socket, *args)
        output_socket.seek(0)
        return output_socket.read()


if __name__ == "__main__":
    main()
