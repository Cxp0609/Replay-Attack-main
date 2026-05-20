#!/usr/bin/env python3
"""
One-time migration script:
1. Moves existing RDF profiles from rdf_profiles/ into rdf_profiles/default/
2. Regenerates each user's RDF profile with foaf:knows links to all other default network members
3. Creates networks.json with all existing users in "default" network
4. Does NOT modify db.json
"""
import os
import json
import shutil
import numpy as np
import glob

# RDF Integration
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from RDF import WebidData, make_rdf_for

RDF_STORE_DIR = "rdf_profiles"
NETWORKS_FILE = "networks.json"
DEFAULT_NETWORK = "default"

def load_networks():
    if os.path.exists(NETWORKS_FILE):
        with open(NETWORKS_FILE, "r") as f:
            return json.load(f)
    return {}

def main():
    print("=== Migration: Move existing users to 'default' network ===\n")

    # Load networks (should already exist from file creation)
    networks = load_networks()
    if DEFAULT_NETWORK not in networks:
        print(f"❌ '{DEFAULT_NETWORK}' network not found in {NETWORKS_FILE}")
        return

    default_members = networks[DEFAULT_NETWORK]
    print(f"Default network has {len(default_members)} members: {default_members}\n")

    # 1. Move existing .ttl files into rdf_profiles/default/
    default_dir = os.path.join(RDF_STORE_DIR, DEFAULT_NETWORK)
    os.makedirs(default_dir, exist_ok=True)

    moved_count = 0
    for ttl_file in glob.glob(os.path.join(RDF_STORE_DIR, "*.ttl")):
        filename = os.path.basename(ttl_file)
        dest = os.path.join(default_dir, filename)
        if not os.path.exists(dest):
            shutil.move(ttl_file, dest)
            print(f"📦 Moved {filename} -> {default_dir}/")
            moved_count += 1
        else:
            print(f"⚠️ {filename} already exists in {default_dir}/, skipping")

    if moved_count == 0:
        print("ℹ️ No .ttl files to move (may already be migrated)")
    else:
        print(f"✅ Moved {moved_count} files")

    # 2. Regenerate RDF profiles with friend links
    print("\n🔄 Regenerating RDF profiles with friend links...")
    for user_id in default_members:
        # Generate random attributes (same pattern as enroll_newuser.py)
        np.random.seed()
        accuracy, speed, reliability = np.random.uniform(size=3)
        x = np.random.randint(2, 6)
        tasks = list(np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], size=x, replace=False))

        # Build friends list: all other default network members
        friends = [other for other in default_members if other != user_id]

        user_profile = WebidData(
            name=user_id,
            accuracy=accuracy,
            speed=speed,
            reliability=reliability,
            tasks=tasks,
            friends=friends
        )

        # Write to network-specific folder
        make_rdf_for(user_profile, folder_name=default_dir, write_to_file=True, print_to_screen=False)
        print(f"  ✅ Regenerated {user_id}.ttl with {len(friends)} friend(s)")

    print(f"\n🎉 Migration complete!")
    print(f"📁 RDF profiles are now in: {default_dir}/")
    print(f"📄 Networks registry: {NETWORKS_FILE}")
    print(f"   Default network members: {len(default_members)} users")

if __name__ == "__main__":
    main()