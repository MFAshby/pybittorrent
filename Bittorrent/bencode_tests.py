from bencode import bdecode, bencode
import unittest
from unittest import TestCase

class TestDecode(TestCase):
    def test_decode(self):
        obj = bdecode("i50e")
        self.assertTrue(obj == 50)

        obj = bdecode("i0e")
        self.assertTrue(obj == 0)

        obj = bdecode("i-500e")
        self.assertTrue(obj == -500)

        obj = bdecode("l4:testi50ee")
        self.assertTrue(obj == ["test", 50])

        obj = bdecode("4:help")
        self.assertTrue(obj == "help")

        obj = bdecode("d4:helpl4:str15:strinee") 
        self.assertTrue(obj == {"help": ["str1", "strin"]})

        obj = bdecode("d4:dic1d3:key3:val4:key24:val2e4:lst1l4:str14:str2ee")
        self.assertTrue(obj == {"dic1":{"key": "val", "key2": "val2"}, "lst1":["str1", "str2"]})

    def test_encode(self):
        enc = bencode(50)
        self.assertTrue(enc == "i50e")

        enc = bencode(0)
        self.assertTrue(enc == "i0e")

        enc = bencode(-500)
        self.assertTrue(enc == "i-500e")

        enc = bencode("help")
        self.assertTrue(enc == "4:help")

        enc = bencode(["test", 50])
        self.assertTrue(enc == "l4:testi50ee")

        enc = bencode({"help": ["str1", "strin"]}) 
        self.assertTrue(enc == "d4:helpl4:str15:strinee")

        enc = bencode({"dic1":{"key": "val", "key2": "val2"}, "lst1":["str1", "str2"]})
        self.assertTrue(enc == "d4:dic1d3:key3:val4:key24:val2e4:lst1l4:str14:str2ee")

if __name__ == '__main__':
    unittest.main()

