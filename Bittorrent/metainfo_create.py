from os.path import getsize
from hashlib import sha1
from bencode import bencode

PIECE_LENGTH = 512

def create(output_filename="",
           filename="", 
           announce_url="http://localhost:8000", 
           comment="Test torrent file", 
           created_by="",
           encoding="UTF-8"):
    """takes a file, creates a metainfo file ready for torrenting"""
    length = getsize(filename)
    pieces = b""

    with open(filename, "rb") as f:
        file_piece = f.read(PIECE_LENGTH)
        while file_piece:
            the_hash = sha1()
            the_hash.update(file_piece)
            pieces += the_hash.digest()
            file_piece = f.read(PIECE_LENGTH)

    
    to_write = {"info": 
                  {"piece length": PIECE_LENGTH,
                    "name": filename,
                    "length": length,
                    "pieces": str(pieces, encoding)},
                "announce":announce_url,
                "creation date": 1000000000,
                "comment": comment,
                "created by": created_by,
                "encoding": encoding}

    with open(output_filename, "w") as f:
        f.write(bencode(to_write))
