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
import requests
import cv2
import numpy as np

from face.detector import detect_faces
from face.encoder import generate_embedding


def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two face embeddings.
    Higher = more similar.
    """
    a = embedding1.flatten().astype(np.float32)
    b = embedding2.flatten().astype(np.float32)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def download_image(url, output_path):
    """Download a candidate image."""

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if not content_type.startswith("image/"):
            return False

        with open(output_path, "wb") as f:
            f.write(response.content)

        return True

    except Exception as e:
        print(f"Download failed: {e}")
        return False


def get_image_urls(candidate):
    """Return image URLs in fallback order: source image, then Lens thumbnail."""
    urls = []
    for key in ("image", "thumbnail"):
        url = (candidate.get(key) or "").strip()
        if url and url not in urls:
            urls.append(url)
    return urls


def compare_faces(image_path, candidates, progress_callback=None):
    """
    Compare the input face against faces found
    in Google Lens candidate images.
    """

    # --------------------------------------------------
    # 1. Read input image
    # --------------------------------------------------

    input_image = cv2.imread(image_path)

    if input_image is None:
        raise FileNotFoundError(
            f"Could not read {image_path}"
        )

    # OpenCV uses BGR, but our detector expects RGB
    input_rgb = cv2.cvtColor(
        input_image,
        cv2.COLOR_BGR2RGB
    )

    input_faces = detect_faces(input_rgb)

    if len(input_faces) == 0:
        raise RuntimeError(
            "No face detected in input image."
        )

    print(
        f"Input image: {len(input_faces)} face(s) detected."
    )

    # Generate embedding for first input face
    input_embedding = generate_embedding(
        input_rgb,
        input_faces[0]
    )

    # --------------------------------------------------
    # 2. Prepare candidate directory
    # --------------------------------------------------

    os.makedirs(
        "data/candidates",
        exist_ok=True
    )

    results = []

    # --------------------------------------------------
    # 3. Process Lens candidates
    # --------------------------------------------------

    for index, candidate in enumerate(candidates, start=1):

        image_urls = get_image_urls(candidate)

        if not image_urls:
            print(f"[{index}] No image URL available.")
            if progress_callback:
                progress_callback(index, len(candidates), candidate)
            continue

        image_path = f"data/candidates/candidate_{index}.jpg"

        print(f"[{index}/{len(candidates)}] Processing candidate...")

        # Some social pages expose an image URL that is blocked while the
        # Google-hosted Lens thumbnail remains downloadable. Try both before
        # discarding the candidate.
        success = False
        image_url = ""
        for candidate_url in image_urls:
            if download_image(candidate_url, image_path):
                success = True
                image_url = candidate_url
                break

        if not success:
            if progress_callback:
                progress_callback(index, len(candidates), candidate)
            continue

        # Read downloaded image
        candidate_image = cv2.imread(
            image_path
        )

        if candidate_image is None:
            if progress_callback:
                progress_callback(index, len(candidates), candidate)
            continue

        candidate_rgb = cv2.cvtColor(
            candidate_image,
            cv2.COLOR_BGR2RGB
        )

        # Detect faces
        candidate_faces = detect_faces(
            candidate_rgb
        )

        if len(candidate_faces) == 0:
            print("    No face detected.")
            if progress_callback:
                progress_callback(index, len(candidates), candidate)
            continue

        best_score = 0.0

        # Compare against every face in candidate
        for face_box in candidate_faces:

            try:
                candidate_embedding = (
                    generate_embedding(
                        candidate_rgb,
                        face_box
                    )
                )

                score = cosine_similarity(
                    input_embedding,
                    candidate_embedding
                )

                best_score = max(
                    best_score,
                    score
                )

            except Exception as e:
                print(
                    f"    Face comparison failed: {e}"
                )

        result = {
            "rank": index,
            "title": candidate.get("title"),
            "source": candidate.get("source"),
            "link": candidate.get("link"),
            "image_url": image_url,
            "faces_detected": len(candidate_faces),
            "similarity": round(best_score, 4),
            "search_sources": candidate.get("search_sources", []),
            "social_targeted": bool(candidate.get("social_targeted", False)),
            "social_query_platform": candidate.get("social_query_platform", ""),
            "discovery_pipeline": candidate.get("discovery_pipeline", "Google Lens"),
        }

        results.append(result)

        print(
            f"    Faces: {len(candidate_faces)} | "
            f"Similarity: {best_score:.4f}"
        )

        if progress_callback:
            progress_callback(
                index,
                len(candidates),
                candidate
            )

    # --------------------------------------------------
    # 4. Sort by similarity
    # --------------------------------------------------

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results


if __name__ == "__main__":

    input_image = "data/test.jpg"

    # Load Lens candidates
    with open(
        "data/lens_candidates.json",
        "r",
        encoding="utf-8"
    ) as f:

        candidates = json.load(f)

    print(
        f"Loaded {len(candidates)} Lens candidates."
    )

    print(
        "\nStarting face verification...\n"
    )

    results = compare_faces(
        input_image,
        candidates
    )

    # Save results
    with open(
        "data/face_match_results.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n================================")
    print("FACE MATCHING COMPLETE")
    print("================================")

    if results:

        print("\nTop 10 matches:\n")

        for result in results[:10]:

            print(
                f"{result['similarity']:.4f} | "
                f"{result['source']} | "
                f"{result['title']}"
            )

            print(
                f"     {result['link']}"
            )

    else:

        print(
            "No candidate faces could be compared."
        )

    print(
        "\nResults saved to:"
    )

    print(
        "data/face_match_results.json"
    )