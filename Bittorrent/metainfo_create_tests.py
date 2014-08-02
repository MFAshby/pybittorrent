from unittest import TestCase
import unittest
from metainfo_create import create
from os.path import getsize

class MetainfoTestCase(TestCase):
    def test_create(self):
        #write a test file... 
        with open("test.file", "w") as f:
            f.write("Testing torrent file!!!")
            for i in range(100000):
                f.write(str(i))

        create(output_filename="test.torrent",
               filename="test.file", 
               announce_url="http://localhost:8000", 
               comment="Test torrent file", 
               created_by="Martin Ashby",
               encoding="iso-8859-15")

if __name__ == "__main__":
    unittest.main()
