import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import json
import hashlib

from blockchain.chain import Blockchain


RESULT_FILE = "data/face_match_results.json"


def create_fingerprint(result):
    """
    Create a deterministic SHA-256 fingerprint
    from the verified social/web result.
    """

    data_string = json.dumps(
        result,
        sort_keys=True,
        ensure_ascii=False
    )

    return hashlib.sha256(
        data_string.encode("utf-8")
    ).hexdigest()


def get_best_match():

    with open(
        RESULT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        results = json.load(f)

    if not results:
        raise RuntimeError(
            "No face matching results found."
        )

    return results[0]


def add_verified_result():

    best_match = get_best_match()

    fingerprint = create_fingerprint(
        best_match
    )

    blockchain = Blockchain()

    blockchain_data = {
        "type": "verified_face_match",
        "title": best_match.get("title"),
        "source": best_match.get("source"),
        "url": best_match.get("link"),
        "similarity": best_match.get("similarity"),
        "fingerprint": fingerprint
    }

    block = blockchain.add_block(
        blockchain_data
    )

    status, message = blockchain.verify_chain()

    return (
        best_match,
        fingerprint,
        block,
        status,
        message
    )


if __name__ == "__main__":

    (
        best_match,
        fingerprint,
        block,
        status,
        message
    ) = add_verified_result()

    print("\n================================")
    print("VERIFIED RESULT")
    print("================================")

    print(
        "Title:",
        best_match.get("title")
    )

    print(
        "Source:",
        best_match.get("source")
    )

    print(
        "Similarity:",
        best_match.get("similarity")
    )

    print(
        "URL:",
        best_match.get("link")
    )

    print("\nSHA-256 Fingerprint:")
    print(fingerprint)

    print("\nBlockchain Block:")
    print("Index:", block.index)
    print("Hash:", block.hash)

    print("\nBlockchain Verification:")
    print("Status:", status)
    print("Message:", message)