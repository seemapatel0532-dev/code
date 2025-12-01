from util import hash256
class Block_header:
    def __init__(self, version, prev_hash, merkle_root, timestamp, bits):
        self.version = version
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0

    def mine(self, target):
        self.hash = ''
        while self.hash[:4] != target * '0':
            self.nonce += 1
            self.hash = hash256((str(self.version) + self.prev_hash + self.merkle_root + str(self.timestamp) + str(self.bits) + str(self.nonce)).encode()).hex()
            print(f"Mining started nonce: {self.nonce} and hash: {self.hash}", end='\r')