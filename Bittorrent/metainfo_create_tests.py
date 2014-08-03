from unittest import TestCase
import unittest
from metainfo_create import create
from io import BytesIO, StringIO
from bencode import bdecode

class MetainfoTestCase(TestCase):
    def test_create(self):
        #mock file-like objects to read and write
        mock_output = StringIO()
        test_bytes = b"Testing file!"
        test_bytes_length = len(test_bytes)
        mock_input = BytesIO(test_bytes)
        
        create(output_file=mock_output,
           input_file=mock_input, 
           input_file_length=test_bytes_length,
           input_file_name="Testing.file",
           piece_length=512000,
           pieces_encoding="iso-8859-15",
           announce_url="http://localhost:8000", 
           comment="Test torrent file", 
           created_by="Martin Ashby's Test script...")

        mock_output.seek(0)
        output_dict = bdecode(mock_output.read())

        #check the output has the appropriate keys.
        info_dict = output_dict.get("info")
        self.assertTrue(len(info_dict))
        self.assertTrue(info_dict.get("piece length") == 512000)
        self.assertTrue(info_dict.get("name") == "Testing.file")
        self.assertTrue(info_dict.get("length") == test_bytes_length)
        self.assertTrue(info_dict.get("pieces"))
        self.assertTrue(output_dict.get("announce") == "http://localhost:8000")
        self.assertTrue(type(output_dict.get("creation date")) == int)
        self.assertTrue(output_dict.get("comment") == "Test torrent file")
        self.assertTrue(output_dict.get("created by") == "Martin Ashby's Test script...")
        self.assertTrue(output_dict.get("encoding") == "iso-8859-15")

if __name__ == "__main__":
    unittest.main()
