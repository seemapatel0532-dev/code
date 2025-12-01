class Block:
    def __init__(self, height, block_header, tx_counts, txs):
        self.height = height
        self.block_header = block_header
        self.tx_counts = tx_counts
        self.txs = txs

