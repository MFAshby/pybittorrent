from bencode import bdecode, bencode
from unittest import TestCase, main

class TestDecode(TestCase):
    def test_decode_int_50(self):
        obj = bdecode("i50e")
        self.assertTrue(obj == 50)

    def test_decode_int_0(self):
        obj = bdecode("i0e")
        self.assertTrue(obj == 0)

    def test_decode_int_neg_500(self):
        obj = bdecode("i-500e")
        self.assertTrue(obj == -500)

    def test_decode_str(self):
        obj = bdecode("4:help")
        self.assertTrue(obj == b"help")

    def test_decode_longer_str(self):
        obj = bdecode("10:0123456789")
        self.assertTrue(obj == b"0123456789")

    def test_decode_really_long_str(self):
        obj = bdecode("55:0123456789012345678901234567890123456789012345678901234")
        self.assertTrue(obj == b"0123456789012345678901234567890123456789012345678901234")

    def test_decode_list(self):
        obj = bdecode("l4:testi50ee")
        self.assertTrue(obj == [b"test", 50])

    def test_decode_dict_simple(self):
        obj = bdecode("d4:helpl4:str15:strinee") 
        self.assertTrue(obj == {b"help": [b"str1", b"strin"]})

    def test_decode_dict_nested(self):
        obj = bdecode("d4:dic1d3:key3:val4:key24:val2e4:lst1l4:str14:str2ee")
        self.assertTrue(obj == {b"dic1":{b"key": b"val", b"key2": b"val2"}, b"lst1":[b"str1", b"str2"]})


class TestEncode(TestCase):
    def test_encode_int_50(self):
        enc = bencode(50)
        self.assertTrue(enc == "i50e")
    def test_encode_int_0(self):
        enc = bencode(0)
        self.assertTrue(enc == "i0e")

    def test_encode_int_neg_500(self):
        enc = bencode(-500)
        self.assertTrue(enc == "i-500e")

    def test_encode_str(self):
        enc = bencode("help")
        self.assertTrue(enc == "4:help")

    def test_encode_list(self):
        enc = bencode(["test", 50])
        self.assertTrue(enc == "l4:testi50ee")

    def test_encode_dict(self):
        enc = bencode({"help": ["str1", "strin"]}) 
        self.assertTrue(enc == "d4:helpl4:str15:strinee")

    def test_encode_nested_dict(self):
        enc = bencode({"dic1":{"key": "val", "key2": "val2"}, "lst1":["str1", "str2"]})
        self.assertTrue(enc == "d4:dic1d3:key3:val4:key24:val2e4:lst1l4:str14:str2ee")

if __name__ == '__main__':
    main()

