import numpy as np
import cv2
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from feature_extractor import extract_feature_vector, load_feature_extractors

# Configuration
CAPTURED_DIR = "captured_images"
LOCAL_DB = "db.json"

def load_enrolled_users():
    """Load enrolled users from db.json."""
    if not os.path.exists(LOCAL_DB):
        print(f"❌ Database file {LOCAL_DB} not found.")
        return []
    with open(LOCAL_DB, "r") as f:
        return json.load(f)

def get_images_for_user(user_id):
    """Get all image paths for a given user_id."""
    images = []
    if not os.path.exists(CAPTURED_DIR):
        return images
    for filename in os.listdir(CAPTURED_DIR):
        if filename.startswith(user_id + "_") and filename.endswith(".png"):
            images.append(os.path.join(CAPTURED_DIR, filename))
    return images

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    a, b = np.array(vec1), np.array(vec2)
    if a.shape != b.shape:
        return np.nan
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

def compute_all_scores(users, fes):
    """
    Compute both legit and replay attack scores, returning raw distances.
    """
    legit_scores = []
    replay_scores = []
    
    for user in users:
        user_id = user["user_id"]
        images = get_images_for_user(user_id)
        
        if not images:
            continue
        
        # Use the first image as reference
        ref_image_path = images[0]
        ref_image = cv2.imread(ref_image_path, cv2.IMREAD_GRAYSCALE)
        if ref_image is None:
            continue
        
        # === Legit scores: same FE on perturbed versions of the same image ===
        for _ in range(5):
            noise = np.random.normal(0, 3.0, ref_image.shape).astype(np.float32)
            perturbed = ref_image.astype(np.float32) + noise
            perturbed = np.clip(perturbed, 0, 255).astype(np.uint8)
            
            for fe_idx in range(len(fes)):
                vec_ref = extract_feature_vector(ref_image, fe_index=fe_idx)
                vec_perturbed = extract_feature_vector(perturbed, fe_index=fe_idx)
                
                if not vec_ref or not vec_perturbed:
                    continue
                
                sim = cosine_similarity(vec_ref, vec_perturbed)
                legit_scores.append(sim)
        
        # === Replay attack scores: different FEs on the exact same image ===
        vectors = []
        for fe_idx in range(len(fes)):
            vec = extract_feature_vector(ref_image, fe_index=fe_idx)
            if vec:
                vectors.append(vec)
        
        for i in range(len(vectors)):
            for j in range(i+1, len(vectors)):
                sim = cosine_similarity(vectors[i], vectors[j])
                replay_scores.append(sim)
    
    return legit_scores, replay_scores

def moving_average_2point(data):
    """Compute 2-point moving average (each point averages current and next)."""
    if len(data) < 2:
        return data
    arr = np.array(data)
    return (arr[:-1] + arr[1:]) / 2.0

def plot_histogram(legit_scores, replay_scores, output_path="similarity_score_distribution.png"):
    """Generate histogram plot using cosine similarity with threshold line."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Use finer bins to distinguish close scores
    bins = np.linspace(0, 1, 50)
    
    # === Main plot (full range) ===
    ax1.hist(legit_scores, bins=bins, alpha=0.7, label='Legit Scores', color='blue', edgecolor='black', linewidth=0.8)
    ax1.hist(replay_scores, bins=bins, alpha=0.7, label='Replay Attacks', color='red', edgecolor='black', linewidth=0.8)
    
    # Compute 2-point moving averages
    legit_sorted = np.sort(legit_scores)
    replay_sorted = np.sort(replay_scores)
    
    ma_legit = moving_average_2point(legit_sorted)
    ma_replay = moving_average_2point(replay_sorted)
    
    x_legit = np.arange(len(ma_legit))
    x_replay = np.arange(len(ma_replay))
    
    ax1.plot(x_legit, ma_legit, color='blue', linewidth=2, label='2 per. Mov. Avg. (Legit Scores)')
    ax1.plot(x_replay, ma_replay, color='red', linewidth=2, label='2 per. Mov. Avg. (Replay Attacks)')
    
    ax1.axvline(x=0.85, color='green', linestyle='--', linewidth=2, label='Threshold (0.85)')
    ax1.set_xlabel('Cosine Similarity', fontsize=12)
    ax1.set_ylabel('Occurrences', fontsize=12)
    ax1.set_title('Similarity Score Distribution (Cosine Similarity)', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    
    # === Zoomed-in plot for legit scores (0.95 - 1.0) ===
    zoom_bins = np.linspace(0.95, 1.0, 100)
    ax2.hist(legit_scores, bins=zoom_bins, alpha=0.7, label='Legit Scores (Zoomed)', color='blue', edgecolor='black', linewidth=0.8)
    ax2.set_xlabel('Cosine Similarity (Zoomed 0.95 - 1.0)', fontsize=12)
    ax2.set_ylabel('Occurrences', fontsize=12)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0.95, 1.0)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Saved histogram to {output_path}")
    plt.show()

def main():
    print("=== Generating Similarity Score Distribution ===\n")
    
    # Load feature extractors
    fes = load_feature_extractors()
    if not fes:
        print("❌ No feature extractors found.")
        return
    print(f"✅ Loaded {len(fes)} feature extractors")
    
    # Load enrolled users
    users = load_enrolled_users()
    if not users:
        print("❌ No enrolled users found in database.")
        return
    print(f"✅ Loaded {len(users)} enrolled users")
    
    # Compute both legit and replay attack scores together
    print("\n📊 Computing legit scores (same person, same FE)...")
    print("   Computing replay attack scores (same image, different FEs)...")
    legit_scores, replay_scores = compute_all_scores(users, fes)
    print(f"   Generated {len(legit_scores)} legit scores")
    if legit_scores:
        print(f"   Legit Range: {min(legit_scores):.4f} - {max(legit_scores):.4f}")
        print(f"   Legit Mean: {np.mean(legit_scores):.4f}")
    print(f"   Generated {len(replay_scores)} replay attack scores")
    if replay_scores:
        print(f"   Replay Range: {min(replay_scores):.4f} - {max(replay_scores):.4f}")
        print(f"   Replay Mean: {np.mean(replay_scores):.4f}")
    
    if not legit_scores or not replay_scores:
        print("\n❌ Insufficient data to generate plot.")
        return
    
    # Plot histogram
    print("\n📈 Generating histogram...")
    plot_histogram(legit_scores, replay_scores)
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()