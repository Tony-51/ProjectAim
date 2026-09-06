import cv2
import numpy as np
import os


MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "face_recognition_sface_2021dec.onnx"
)


_MODEL = None


def load_model():
    """
    Load SFace once and reuse it.
    """

    global _MODEL

    if _MODEL is None:

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"SFace model not found at: {MODEL_PATH}"
            )

        _MODEL = cv2.FaceRecognizerSF.create(
            MODEL_PATH,
            ""
        )

    return _MODEL


def normalize_embedding(embedding):
    """
    L2-normalize the face embedding.

    This makes cosine similarity more stable.
    """

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:
        raise ValueError(
            "Face embedding has zero norm."
        )

    return embedding / norm


def generate_embedding(image, face_box):
    """
    Generate a normalized SFace embedding.

    face_box is expected to be the complete YuNet
    face detection output, including the 5 landmarks.
    """

    if image is None:
        raise ValueError(
            "Image is None."
        )

    face = np.asarray(
        face_box,
        dtype=np.float32
    ).reshape(-1)

    # YuNet normally returns:
    #
    # x, y, w, h,
    # left_eye_x, left_eye_y,
    # right_eye_x, right_eye_y,
    # nose_x, nose_y,
    # left_mouth_x, left_mouth_y,
    # right_mouth_x, right_mouth_y,
    # confidence
    #
    # SFace alignCrop needs the complete face
    # detection including landmarks.

    if len(face) < 14:
        raise ValueError(
            f"Invalid face box. "
            f"Expected YuNet detection with landmarks, "
            f"got {len(face)} values."
        )

    model = load_model()

    try:

        aligned_face = model.alignCrop(
            image,
            face
        )

    except Exception as e:

        raise RuntimeError(
            f"Face alignment failed: {e}"
        )

    if aligned_face is None:
        raise RuntimeError(
            "SFace returned an empty aligned face."
        )

    try:

        embedding = model.feature(
            aligned_face
        )

    except Exception as e:

        raise RuntimeError(
            f"SFace feature extraction failed: {e}"
        )

    if embedding is None:
        raise RuntimeError(
            "SFace returned an empty embedding."
        )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    # Ensure consistent shape.
    embedding = embedding.reshape(
        1, -1
    )

    # Normalize.
    embedding = normalize_embedding(
        embedding
    )

    return embedding