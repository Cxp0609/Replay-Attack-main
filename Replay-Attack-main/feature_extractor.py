import numpy as np
import cv2
import os
import re

FE_FILE = "disposable FEs.txt"
FEs = []

# === Standard face size for normalization ===
# The GA-evolved coordinates were likely optimized for ~128x128 faces
FACE_SIZE = 128

# === Load FEs from File ===
def load_feature_extractors():
    global FEs
    if FEs:  # Already loaded
        return FEs

    if not os.path.exists(FE_FILE):
        print(f"❌ FE file '{FE_FILE}' not found.")
        return []

    with open(FE_FILE, 'r') as f:
        content = f.read()

    blocks = content.split("Evaluations: 1000")
    for block in blocks[1:]:
        if "Best:" in block:
            best_start = block.index("Best:") + len("Best:")
            numbers_str = block[best_start:].strip().replace("\n", " ").split()
            numbers = []

            for token in numbers_str:
                try:
                    numbers.append(float(token))
                except ValueError:
                    break

            if len(numbers) >= 74:
                fe = {
                    "x": numbers[0:24],
                    "y": numbers[24:48],
                    "thresholds": numbers[48:72],
                    "radius_w": int(numbers[72]),
                    "radius_h": int(numbers[73])
                }
                FEs.append(fe)
    return FEs


# === Preprocessing: Illumination Normalization ===
def preprocess_face(face_gray):
    """
    Normalize illumination of a grayscale face image.

    Steps:
    1. Resize to standard face size (coordinates were evolved for specific dimensions)
    2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to reduce lighting variation
    3. Apply mild Gaussian blur to reduce noise
    """
    if face_gray is None or face_gray.size == 0:
        return face_gray

    # Step 1: Resize to standard face size
    face_resized = cv2.resize(face_gray, (FACE_SIZE, FACE_SIZE), interpolation=cv2.INTER_LINEAR)

    # Step 2: CLAHE for illumination normalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    face_norm = clahe.apply(face_resized)

    # Step 3: Mild Gaussian blur to reduce noise
    face_norm = cv2.GaussianBlur(face_norm, (3, 3), 0.5)

    return face_norm


# === Patch-Based Feature Extraction ===
def extract_feature_vector(image, fe_index=0):
    """
    Extracts a patch-based feature vector from a grayscale image using the selected FE.

    Improvements over the original version:
    - Preprocesses the face (resize + CLAHE) so coordinates map to consistent facial landmarks
    - Uses richer patch descriptors (histogram of oriented gradients + mean + std)
    - L2-normalizes the output feature vector for fair cosine similarity
    """
    if image is None:
        return []

    fes = load_feature_extractors()
    if not fes:
        print("❌ No FEs loaded.")
        return []

    fe = fes[fe_index % len(fes)]
    x_coords = fe["x"]
    y_coords = fe["y"]
    thresholds = fe["thresholds"]
    rw, rh = fe["radius_w"], fe["radius_h"]

    # Preprocess face: resize to standard size + illumination normalization
    face = preprocess_face(image)
    if face is None:
        return []

    h, w = face.shape
    fv = []

    for x, y, t in zip(x_coords, y_coords, thresholds):
        if t <= 0.4999:
            # Append a small non-zero value to maintain feature dimension parity
            fv.extend([0.0, 0.0, 0.0])
            continue

        x, y = int(round(x)), int(round(y))
        x1, y1 = max(0, x - rw), max(0, y - rh)
        x2, y2 = min(w, x + rw), min(h, y + rh)

        patch = face[y1:y2, x1:x2]
        if patch.size == 0:
            fv.extend([0.0, 0.0, 0.0])
            continue

        # === Enhanced patch descriptor (3 values per patch) ===
        # 1. Mean pixel intensity (original feature)
        mean_val = float(np.mean(patch))

        # 2. Standard deviation (captures texture/contrast within the patch)
        std_val = float(np.std(patch))

        # 3. Gradient magnitude mean (edge information, illumination invariant)
        grad_x = cv2.Sobel(patch, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(patch, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        grad_mean = float(np.mean(grad_mag))

        fv.extend([mean_val, std_val, grad_mean])

    # === L2 Normalize the feature vector ===
    fv = np.array(fv, dtype=np.float64)
    norm = np.linalg.norm(fv)
    if norm > 0:
        fv = (fv / norm).tolist()
    else:
        fv = fv.tolist()

    return fv


# === Legacy simple mean patch extractor (backward compatible) ===
def extract_feature_vector_simple(image, fe_index=0):
    """
    Original simpler version: just patch means with preprocessing.
    Retained for comparison/debugging.
    """
    if image is None:
        return []

    fes = load_feature_extractors()
    if not fes:
        print("❌ No FEs loaded.")
        return []

    fe = fes[fe_index % len(fes)]
    x_coords = fe["x"]
    y_coords = fe["y"]
    thresholds = fe["thresholds"]
    rw, rh = fe["radius_w"], fe["radius_h"]

    # Preprocess
    face = preprocess_face(image)
    if face is None:
        return []

    h, w = face.shape
    fv = []

    for x, y, t in zip(x_coords, y_coords, thresholds):
        if t <= 0.4999:
            fv.append(0.0)
            continue

        x, y = int(round(x)), int(round(y))
        x1, y1 = max(0, x - rw), max(0, y - rh)
        x2, y2 = min(w, x + rw), min(h, y + rh)

        patch = face[y1:y2, x1:x2]
        avg = float(np.mean(patch)) if patch.size > 0 else 0.0
        fv.append(avg)

    # L2 normalize
    fv = np.array(fv, dtype=np.float64)
    norm = np.linalg.norm(fv)
    if norm > 0:
        fv = (fv / norm).tolist()
    else:
        fv = fv.tolist()

    return fv