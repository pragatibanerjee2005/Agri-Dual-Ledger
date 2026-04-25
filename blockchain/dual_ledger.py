import hashlib
import json
from datetime import datetime


class Block:

    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = str(datetime.now())
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:

    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), data, previous_block.hash)
        self.chain.append(new_block)


# Create two ledgers
public_ledger = Blockchain()
private_ledger = Blockchain()


# Example public transaction
public_data = {
    "crop": "Rice",
    "district": "Malda",
    "yield": 1040,
    "fraud_score": 8.4
}

# Example private transaction
private_data = {
    "farmer_id": "WB10234",
    "bank_account": "XXXX1234",
    "subsidy_amount": 5000
}


public_ledger.add_block(public_data)
private_ledger.add_block(private_data)


print("PUBLIC LEDGER")
for block in public_ledger.chain:
    print(block.__dict__)


print("\nPRIVATE LEDGER")
for block in private_ledger.chain:
    print(block.__dict__)