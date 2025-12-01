from block import Block
from block_header import Block_header
from database import Blockchain_db
import time
import json

VERSION = 1
ZERO_HASH = '0' * 64

class Blockchain:
    def __init__(self):
        self.genesis_block()

    def fetch_last_block(self):
        blockckain_db = Blockchain_db()
        return blockckain_db.last_block()
    
    def write_on_disk(self, block):
        blockckain_db = Blockchain_db()
        return blockckain_db.write(block)

    def genesis_block(self):
        self.add_block(0, ZERO_HASH)

    def add_block(self, block_height, prev_hash):
        timestamp = int(time.time())
        merkle_root = ''
        bits = ''
        block_header = Block_header(VERSION, prev_hash, merkle_root, timestamp, bits)
        # block_header.mine(4)
        txs = 'hello'
        self.write_on_disk([Block(block_height, block_header.__dict__, len(txs), txs).__dict__])

if __name__ == '__main__':
    blockchain = Blockchain()
    last_block = blockchain.fetch_last_block()
    print(json.dumps(last_block))
    blockchain.add_block(last_block['height'] + 1, last_block['block_header']['hash'])
    print(json.dumps(last_block))