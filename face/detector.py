import cv2
import numpy as np
import os


MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "face_detection_yunet_2023mar.onnx"
)


def detect_faces(image):
    """
    Detect faces using OpenCV YuNet.

    Returns face detections in the format expected
    by OpenCV SFace:
        [x, y, width, height,
         right_eye_x, right_eye_y,
         left_eye_x, left_eye_y,
         nose_x, nose_y,
         right_mouth_x, right_mouth_y,
         left_mouth_x, left_mouth_y,
         confidence]
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"YuNet model not found at: {MODEL_PATH}"
        )

    height, width = image.shape[:2]

    detector = cv2.FaceDetectorYN.create(
        MODEL_PATH,
        "",
        (width, height),
        0.6,
        0.3,
        5000
    )

    # YuNet expects BGR
    if len(image.shape) == 3:
        bgr_image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR
        )
    else:
        bgr_image = image

    _, faces = detector.detect(bgr_image)

    if faces is None:
        return np.empty((0, 15), dtype=np.float32)

    return faces