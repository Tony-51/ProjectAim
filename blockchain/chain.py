import json
import os
import time

from blockchain.block import Block


BLOCKCHAIN_FILE = "data/blockchain.json"


class Blockchain:

    def __init__(self):
        self.chain = []
        self.load_chain()

    # ------------------------------
    # Genesis Block
    # ------------------------------

    def create_genesis_block(self):

        genesis = Block(
            index=0,
            timestamp=time.time(),
            data={
                "message": "Genesis Block"
            },
            previous_hash="0" * 64,
        )

        self.chain.append(genesis)
        self.save_chain()

    # ------------------------------
    # Load Existing Chain
    # ------------------------------

    def load_chain(self):

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(BLOCKCHAIN_FILE):
            self.create_genesis_block()
            return

        with open(BLOCKCHAIN_FILE, "r") as f:
            chain_data = json.load(f)

        for block_data in chain_data:
            block = Block(
                block_data["index"],
                block_data["timestamp"],
                block_data["data"],
                block_data["previous_hash"],
            )

            block.hash = block_data["hash"]

            self.chain.append(block)

    # ------------------------------
    # Save Blockchain
    # ------------------------------

    def save_chain(self):

        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(
                [block.to_dict() for block in self.chain],
                f,
                indent=4,
            )

    # ------------------------------
    # Add Block
    # ------------------------------

    def add_block(self, data):

        previous_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
        )

        self.chain.append(new_block)

        self.save_chain()

        return new_block

    # ------------------------------
    # Verify Blockchain
    # ------------------------------

    def verify_chain(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False, f"Block {i} has been modified."

            if current.previous_hash != previous.hash:
                return False, f"Block {i} previous hash mismatch."

        return True, "Blockchain verified successfully."