#encoding and decoding in bittorrent encode (bencode)

import string
import io

class BencodeError(BaseException):
    def __init__(self, error):
        self.error = error
    def __repr__(self):
        return self.error

def bdecode_file(input_file):
    #read first byte, turn it in to a character.
    b = read_one_chr(input_file)
    if b == 'd':
        return read_dict(input_file)
    elif b == 'l':
        return read_list(input_file)
    elif b == 'i':
        return read_int(input_file)
    else:
        #seek back one, we need that first char as part of the string length.
        input_file.seek(-1, io.SEEK_CUR)
        return read_bytes_str(input_file)

def read_dict(input_file):
    d = {}
    while True:
        if read_one_chr(input_file) == 'e': #test if we got to the end of the dict yet.
            return d
        input_file.seek(-1, io.SEEK_CUR)  #go back one, as we read one in...
        key = read_bytes_str(input_file)  #decode a key object, always a string
        value = bdecode_file(input_file)  #decode a value object
        d[key] = value                    #add to the dictionary

def read_list(input_file):
    l = []
    while True:
        if read_one_chr(input_file) == 'e': #test if we got to the end of the list yet.
            return l
        input_file.seek(-1, io.SEEK_CUR) #go back one, as we read one in...
        item = bdecode_file(input_file)  #decode a list item
        l.append(item)                   #add to the lit    

def read_int(input_file, end_chr='e'):   #specify end char, used in read string too
    num_chrs = ""
    input_chr = read_one_chr(input_file)
    while input_chr != end_chr:
        num_chrs += input_chr
        input_chr = read_one_chr(input_file)
    return int(num_chrs, base=10)

def read_bytes_str(input_file):
    length = read_int(input_file, end_chr=":") #int length, separated by : from string chars
    return input_file.read(length)

def read_one_chr(input_file):
    input_bytes = input_file.read(1)
    if not input_bytes:
        raise BencodeError("Unexpected end of file!")
    return chr(input_bytes[0])

def bdecode(input_str, encoding="UTF-8"):
    from io import BytesIO
    input_bytes = input_str.encode(encoding)
    input_file = BytesIO(input_bytes)
    return bdecode_file(input_file)

def bencode_file(output_file, root):
    if type(root) is str:
        write_str(output_file, str(len(root)))
        write_str(output_file, ":")
        write_str(output_file, root)
    elif type(root) is bytes:
        write_str(output_file, str(len(root)))
        write_str(output_file, ":")
        output_file.write(root)
    elif type(root) is int:
        write_str(output_file, "i")
        write_str(output_file, str(root))
        write_str(output_file, "e")
    elif type(root) is list:
        write_str(output_file, "l")
        for item in root:
            bencode_file(output_file, item)
        write_str(output_file, "e")
    elif type(root) is dict:
        write_str(output_file, "d")
        #keys must be sorted, using utf-8 bytes
        for the_key in sorted(root.keys(), key=utf8bytes):
            bencode_file(output_file, the_key)
            bencode_file(output_file, root[the_key])
        write_str(output_file, "e")
    else:
        raise BencodeError("Invalid input:" + str(root))

def utf8bytes(to_encode):
    return bytes(to_encode, "UTF-8")

def write_str(output_file, string):
    output_file.write(string.encode("UTF-8"))

def bencode(obj, encoding="UTF-8"):
    from io import BytesIO
    output_file = BytesIO()
    bencode_file(output_file, obj)
    output_file.seek(0)
    return str(output_file.read(), encoding)

#if running this as main, take an input and print the output python object
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Decode using bittorrent encoding.')
    parser.add_argument('input', type=str, help='input string to be decoded, or the file to read input from (with -f option)')
    parser.add_argument('-f', dest="read_file", action='store_const', default=0, const=1, help='read input from a file')

    args = parser.parse_args()
    if args.read_file:
        with open(args.input, 'rb') as the_file:
            print(bdecode_file(the_file))
    else:
        print(bdecode(args.input))





