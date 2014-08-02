# -*- coding: utf-8 -*-

#encoding and decoding in bittorrent encode (bencode)
#totally ripped straight from
#https://wiki.theory.org/Decoding_bencoded_data_with_python

import re
try:
    import psyco  # Optional, 2.5x improvement in speed
    psyco.full()
except ImportError:
    pass

class BencodeError(BaseException):
    def __init__(self, error):
        self.error = error
    def __repr__(self):
        return self.error

#bencoding specification states that dictionaries must be encoded with string keys in sorted order, 
#using byte representation of the string to sort. This function is used to get the sorting key.
def utf8bytes(to_encode):
    return bytes(to_encode, "UTF-8")

decimal_match = re.compile('\d')

def bdecode(data):
    chunks = list(data)
    chunks.reverse()
    root = _dechunk(chunks)
    return root

def _dechunk(chunks):
    item = chunks.pop()
    if item == 'd':
        item = chunks.pop()
        dct = {}
        while item != 'e':
            chunks.append(item)
            key = _dechunk(chunks)
            dct[key] = _dechunk(chunks)
            item = chunks.pop()
        return dct
    elif item == 'l':
        item = chunks.pop()
        lst = []
        while item != 'e':
            chunks.append(item)
            lst.append(_dechunk(chunks))
            item = chunks.pop()
        return lst
    elif item == 'i':
        item = chunks.pop()
        num = ''
        while item != 'e':
            num += item
            item = chunks.pop()
        return int(num)
    elif decimal_match.search(item):
        #todo strings may not always be UTF-8 encoded! Return as bytes...
        num = ''
        while decimal_match.search(item):
            num += item
            item = chunks.pop()
        line = ""
        for i in range(int(num)):
            line += chunks.pop()
        return line
    raise BencodeError("Invalid input:" + str(item))

def bencode(root):
    if type(root) is str:
        return str(len(root)) + ":" + root
    elif type(root) is int:
        return "i" + str(root) + "e"
    elif type(root) is list:
        ret = "l"
        for item in root:
            ret = ret + bencode(item)
        return ret + "e"
    elif type(root) is dict:
        ret = "d"
        #keys must be sorted, using utf-8 bytes
        for the_key in sorted(root.keys(), key=utf8bytes):
            ret = ret + bencode(the_key) + bencode(root[the_key])
        return ret + "e"
    else:
        raise BencodeError("Invalid input:" + str(root))

#if running this as main, take an input and print the output python object
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Decode using bittorrent encoding.')
    parser.add_argument('input', type=str, help='input string to be decoded, or the file to read input from (with -f option)')
    parser.add_argument('-f', dest="read_file", action='store_const', default=0, const=1, help='read input from a file')
    parser.add_argument('-e', dest="encoding", type=str, default="UTF-8", help='encoding for the input file (Defaults to UTF-8)')

    args = parser.parse_args()
    if args.read_file:
        with open(args.input, 'r', encoding=args.encoding) as the_file:
            the_input = the_file.read()
    else:
        the_input = args.input

    print(bdecode(the_input))






