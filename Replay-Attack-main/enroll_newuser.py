import cv2
import os
import json
import time
import numpy as np
from feature_extractor import extract_feature_vector, load_feature_extractors

# RDF Integration
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from RDF import WebidData, make_rdf_for

# === Configuration ===
CAPTURED_DIR = "captured_images"
LOCAL_DB = "db.json"
RDF_STORE_DIR = "rdf_profiles"
NETWORKS_FILE = "networks.json"

os.makedirs(CAPTURED_DIR, exist_ok=True)
os.makedirs(RDF_STORE_DIR, exist_ok=True)

# === Network Registry Functions ===
def load_networks():
    """Load the networks registry (networks.json)."""
    if os.path.exists(NETWORKS_FILE):
        with open(NETWORKS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("❌ Invalid JSON in networks.json, starting fresh.")
    return {"default": []}

def save_networks(networks):
    """Save the networks registry to disk."""
    with open(NETWORKS_FILE, "w") as f:
        json.dump(networks, f, indent=2)
    print(f"💾 Saved networks registry with {sum(len(v) for v in networks.values())} users across {len(networks)} network(s).")

def select_network():
    """Prompt the user to select or create a network. Returns the chosen network name."""
    networks = load_networks()

    # Build list of available networks (exclude empty numbered ones from display unless user creates them)
    available = list(networks.keys())

    print("\n--- Available Networks ---")
    if available:
        for i, net in enumerate(available, 1):
            count = len(networks[net])
            print(f"  {i}. {net} ({count} member{'s' if count != 1 else ''})")
    else:
        print("  (no networks exist yet)")

    print(f"  N. Create a new network")
    print(f"  D. Use default network")
    print("--------------------------")

    choice = input("Select network by name, number, or 'N'/'D': ").strip().lower()

    # Handle number input
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            selected = available[idx]
            print(f"📡 Joined existing network: {selected}")
            return selected
        else:
            print(f"❌ Invalid selection. Using default network.")
            return "default"

    # Handle 'new' / 'n'
    if choice in ('n', 'new'):
        new_name = input("Enter new network name (e.g., 003): ").strip()
        if not new_name:
            print("❌ Network name cannot be empty. Using default.")
            return "default"
        if new_name in networks:
            print(f"ℹ️ Network '{new_name}' already exists. Joining it.")
        else:
            networks[new_name] = []
            save_networks(networks)
            print(f"🆕 Created new network: {new_name}")
        return new_name

    # Handle 'default' / 'd'
    if choice in ('d', 'default'):
        print(f"📡 Using default network.")
        return "default"

    # Try to match by exact name
    if choice in networks:
        print(f"📡 Joined existing network: {choice}")
        return choice

    # Fallback
    print(f"❌ Network '{choice}' not found. Using default network.")
    return "default"

def add_user_to_network(network_name, user_id):
    """Add a user to a network and update the networks.json file."""
    networks = load_networks()
    if network_name not in networks:
        networks[network_name] = []
    if user_id not in networks[network_name]:
        networks[network_name].append(user_id)
        save_networks(networks)
    return networks

def get_network_members(network_name):
    """Get all members of a network (excluding the given user)."""
    networks = load_networks()
    return networks.get(network_name, [])

def regenerate_network_rdfs(network_name, exclude_user=None):
    """
    Regenerate RDF profiles for all members of a network so their friend lists
    stay in sync. This is called after adding a new user to an existing network.
    """
    networks = load_networks()
    members = networks.get(network_name, [])
    network_dir = os.path.join(RDF_STORE_DIR, network_name)

    for user_id in members:
        if user_id == exclude_user:
            continue  # Skip the newly added user (their profile was just created)

        # Generate random attributes
        np.random.seed()
        accuracy, speed, reliability = np.random.uniform(size=3)
        x = np.random.randint(2, 6)
        tasks = list(np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], size=x, replace=False))

        # Friends = all other members of the same network
        friends = [other for other in members if other != user_id]

        user_profile = WebidData(
            name=user_id,
            accuracy=accuracy,
            speed=speed,
            reliability=reliability,
            tasks=tasks,
            friends=friends
        )

        make_rdf_for(user_profile, folder_name=network_dir, write_to_file=True, print_to_screen=False)

    print(f"🔄 Regenerated RDF profiles for {len(members) - (1 if exclude_user else 0)} existing members in network '{network_name}'.")

# === Existing Functions ===
def save_local_db(db):
    with open(LOCAL_DB, "w") as f:
        json.dump(db, f, indent=2)
    print(f"💾 Saved database with {len(db)} users.")

def load_local_db():
    if os.path.exists(LOCAL_DB):
        with open(LOCAL_DB, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("❌ Invalid JSON in db.json, starting fresh.")
    return []

def capture_face():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Cannot open webcam.")
        return None

    print("📸 Press SPACE to capture your face image.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from webcam.")
            break

        cv2.imshow("Enroll - Press SPACE to capture", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE pressed
            cap.release()
            cv2.destroyAllWindows()
            return frame
        elif key == 27:  # ESC pressed
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

def main():
    print("=== Enroll New User ===")
    user_id = input("Enter user ID (e.g., user123): ").strip()
    if not user_id:
        print("❌ User ID cannot be empty.")
        return

    # === Network Selection (before face capture) ===
    network_name = select_network()
    print(f"📡 Will join network: {network_name}")

    image = capture_face()
    if image is None:
        print("❌ No image captured.")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # For enrollment, you might want to detect face and crop it here
    # For simplicity, let's assume entire gray image is face
    face = gray

    # === Extract feature vectors for ALL available disposable FEs ===
    fes = load_feature_extractors()
    if not fes:
        print("❌ No feature extractors loaded.")
        return

    all_feature_vectors = {}
    lbp_vector = None

    for fe_index in range(len(fes)):
        fv = extract_feature_vector(face, fe_index=fe_index)
        if fv:
            all_feature_vectors[str(fe_index)] = fv
            print(f"  ✅ Extracted feature vector for FE {fe_index} (dim={len(fv)})")
        else:
            print(f"  ❌ Failed to extract feature vector for FE {fe_index}")

    if not all_feature_vectors:
        print("❌ Failed to extract any feature vectors.")
        return

    db = load_local_db()
    # Add new user or update existing
    updated = False
    for entry in db:
        if entry.get("user_id") == user_id:
            entry["feature_vectors"] = all_feature_vectors
            # Keep backward compatibility with single feature_vector field
            entry["feature_vector"] = all_feature_vectors.get("0", [])
            updated = True
            print(f"🔄 Updated feature vectors for user {user_id} ({len(all_feature_vectors)} FEs).")
            break

    if not updated:
        db.append({
            "user_id": user_id,
            "feature_vector": all_feature_vectors.get("0", []),
            "feature_vectors": all_feature_vectors
        })
        print(f"➕ Added new user {user_id} to database with {len(all_feature_vectors)} FE vectors.")

    save_local_db(db)

    # Save captured face image as record
    timestamp = int(time.time())
    filename = os.path.join(CAPTURED_DIR, f"{user_id}_{timestamp}.png")
    cv2.imwrite(filename, face)
    print(f"🖼 Saved captured face image to {filename}")

    # === Add user to network ===
    networks = add_user_to_network(network_name, user_id)
    members = networks.get(network_name, [])
    network_dir = os.path.join(RDF_STORE_DIR, network_name)
    os.makedirs(network_dir, exist_ok=True)

    # === AUTO GENERATE RDF WEBID PROFILE ===
    np.random.seed()
    accuracy, speed, reliability = np.random.uniform(size=3)
    x = np.random.randint(2, 6)
    tasks = list(np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], size=x, replace=False))

    # Friends = all other members of the same network
    friends = [other for other in members if other != user_id]

    user_profile = WebidData(
        name=user_id,
        accuracy=accuracy,
        speed=speed,
        reliability=reliability,
        tasks=tasks,
        friends=friends
    )

    # Generate RDF WebID profile in network-specific folder
    make_rdf_for(user_profile, folder_name=network_dir, write_to_file=True, print_to_screen=False)
    rdf_output_path = os.path.join(network_dir, f"{user_profile.name.zfill(2)}.ttl")
    print(f"🔐 Generated RDF WebID profile: {rdf_output_path}")
    print(f"👥 User has {len(friends)} friend(s) in network '{network_name}': {friends}")

    # === Regenerate existing members' RDF profiles to include this new user ===
    if len(members) > 1:
        regenerate_network_rdfs(network_name, exclude_user=user_id)

if __name__ == "__main__":
    main()