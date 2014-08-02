
#unit tests
import unittest
from unittest.mock import Mock
import tracker

class TestAnnounceUrl(unittest.TestCase):
    def test_request(self):
        #set up a request handler with a mock input for testing. 
        wfile = Mock()
        request_version = "HTTP/1.0"
        requestline = "test"
        path = "http://localhost:8000/announce?peer_id=TESTPEERID&info_hash=TESTINFOHASH&port=8001"
        client_address = ("localhost", 8001)
        test_tracker = tracker.tracker(wfile, path, client_address, requestline, request_version)
        test_tracker.do_GET()
        #assert stuff about test result here!

if __name__ == "__main__":
    unittest.main()
