from os.path import getsize
from hashlib import sha1
from bencode import bencode
from time import time

def create(output_file="",
           input_file=None, 
           input_file_length=0,
           input_file_name="",
           piece_length=512000,
           pieces_encoding="iso-8859-15",
           announce_url="http://localhost:8000", 
           comment="Test torrent file", 
           created_by=""):
    """takes an input file, creates a metainfo file ready for torrenting"""
    pieces = bytearray()
    file_piece = input_file.read(piece_length)
    while file_piece:
        the_hash = sha1()
        the_hash.update(file_piece)
        pieces += the_hash.digest()
        file_piece = input_file.read(piece_length)

    to_write = {"info": 
                  {"piece length": piece_length,
                    "name": input_file_name,
                    "length": input_file_length,
                    "pieces": pieces.decode(encoding=pieces_encoding)},
                "announce":announce_url,
                "creation date": int(time()),
                "comment": comment,
                "created by": created_by,
                "encoding": pieces_encoding}
    to_write_str = bencode(to_write)
    output_file.write(to_write_str)

if __name__ == "__main__":
    import argparse
    from os.path import getsize
    parser = argparse.ArgumentParser(description='Create a metainfo file (.torrent)')
    parser.add_argument('INFILE', type=str, help='the file you want to seed')
    parser.add_argument('OUTFILE', type=str, help='output (.torrent) file')
    parser.add_argument('URL', type=str, help='URL where the tracker is based')
    parser.add_argument('-c', dest="comment", type=str, default="", help='File description')
    parser.add_argument('-w', dest="created_by", type=str, default="", help='Who created this torrent')
    parser.add_argument('-l', dest="piece_length", type=int, default=512000, help='length of pieces (default to 512kB')
    parser.add_argument('-e', dest="piece_encoding", type=str, default="iso-8859-15", help='string encoding for the pieces hash (default iso-8859-15)')

    args = parser.parse_args()
    with open(args.INFILE, "rb") as in_file, open(args.OUTFILE, "w") as out_file:
        in_file_size = getsize(args.INFILE)
        create(output_file=out_file,
               input_file=in_file, 
               input_file_length=in_file_size,
               input_file_name=args.INFILE,
               piece_length=args.piece_length,
               pieces_encoding=args.piece_encoding,
               announce_url=args.URL, 
               comment=args.comment, 
               created_by=args.created_by)


