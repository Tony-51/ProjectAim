from blockchain.chain import Blockchain

blockchain = Blockchain()

data = {
    "title": "Instagram Post",
    "source": "Instagram",
    "url": "https://instagram.com/example",
    "similarity": 0.9116,
}

block = blockchain.add_block(data)

print("\nNEW BLOCK ADDED\n")

print("Index:", block.index)
print("Previous Hash:", block.previous_hash)
print("Current Hash:", block.hash)

status, message = blockchain.verify_chain()

print("\nVerification")
print(status)
print(message)