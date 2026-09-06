import cv2
import numpy as np

from face.detector import detect_faces
from face.encoder import generate_embedding


IMAGE_PATH = "data/test.jpg"


def cosine_similarity(a, b):

    a = a.flatten().astype(np.float32)
    b = b.flatten().astype(np.float32)

    return float(
        np.dot(a, b) /
        (
            np.linalg.norm(a) *
            np.linalg.norm(b)
        )
    )


print("=" * 60)
print("SFACE SELF-SIMILARITY TEST")
print("=" * 60)

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError(
        f"Could not read {IMAGE_PATH}"
    )

image_rgb = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)

faces = detect_faces(
    image_rgb
)

print(
    f"Faces detected: {len(faces)}"
)

if len(faces) == 0:
    raise RuntimeError(
        "No face detected."
    )

face = faces[0]

embedding1 = generate_embedding(
    image_rgb,
    face
)

embedding2 = generate_embedding(
    image_rgb,
    face
)

print(
    "Embedding 1 shape:",
    embedding1.shape
)

print(
    "Embedding 2 shape:",
    embedding2.shape
)

similarity = cosine_similarity(
    embedding1,
    embedding2
)

print()
print(
    f"SELF SIMILARITY: {similarity:.6f}"
)

print()

if similarity > 0.99:

    print(
        "PASS: Encoder is internally consistent."
    )

else:

    print(
        "WARNING: Encoder produced an unexpectedly "
        "low self-similarity."
    )

print("=" * 60)