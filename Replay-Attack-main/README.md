# Replay-Attack Face Recognition & Trust Network System

A real-time face recognition system designed to test replay-attack vulnerabilities, combined with an Erdős–Rényi trust network evaluation tool that generates/imports WebID/RDF profiles for authenticated users.

This project has **two major subsystems**:
1. **Face Recognition + Replay Attack Testing** (client-server, feature extractors, enrollment)
2. **Trust Network Evaluation with WebID/RDF Profiles** (Erdős–Rényi networks, multi-factor ranking, RDF exchange)

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [File-by-File Reference](#file-by-file-reference)
5. [Database Schema](#database-schema)
6. [RDF Profile Structure](#rdf-profile-structure)
7. [Networks Registry](#networks-registry)
8. [Workflow Guide](#workflow-guide)
9. [Security Notes](#security-notes)
10. [Known Issues / Limitations](#known-issues--limitations)

---

## System Architecture

```
┌─────────────┐  WebSocket (port 5002)   ┌─────────────┐
│  CLIENT.py   │ ───────────────────────▶ │  server.py   │
│  (captures)  │                          │  (matches)    │
└──────┬──────┘                           └──────┬──────┘
       │                                          │
       ▼                                          ▼
feature_extractor.py                       db.json (feature DB)
(loads FEs, extracts)                      networks.json (registry)
                                           rdf_profiles/ (RDF store)
                                           received_vectors/ (audit)
```

### Subsystem 1: Face Recognition + Replay Attacks
- **Client** (`CLIENT.py`) captures a face via webcam, crops faces using Haar cascades, extracts **30 patch-based feature vectors** (24 values each) plus 1 LBP vector, computes local matches, and sends everything to the server with a SHA-256 token.
- **Server** (`server.py`) validates the token, matches each vector against `db.json` using cosine similarity (threshold 0.85), and returns per-FE results plus the final decision. If granted, it also returns the user's **RDF WebID profile** from `rdf_profiles/<network>/<user>.ttl`.
- **Replay simulator** (`Replay_simulator.py`) replays stored feature vectors from `db.json` to test whether the system can be spoofed.

### Subsystem 2: Trust Network Evaluation
- **`RDF.py`** generates Erdős–Rényi networks (N=45 nodes, 25 p-values from 0.2 to 1.0, 12 reps each = 300 networks), decorates nodes with random `accuracy`, `speed`, `reliability`, and `tasks`, then ranks each node using a **weighted multi-factor score** covering centrality, core number, performance, assortativity, and degree.
- **`enroll_newuser.py`** and **`server.py`** use `RDF.py` functions to generate/read **WebID RDF profiles** (Turtle format) — each user gets a `.ttl` file with performance attributes, task assignments, and `foaf:knows` links to network friends.

---

## Prerequisites

- Python 3.8+
- Packages:
  ```
  numpy
  opencv-python (cv2)
  networkx
  matplotlib
  seaborn
  scikit-image (skimage)
  rdflib
  ```
- Optional: Git for version control

---

## Quick Start

### 1. Face Recognition (Server + Client)

```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Capture a face and authenticate
python CLIENT.py

# Terminal 3: Simulate a replay attack (optional)
python Replay_simulator.py --user Chris
```

### 2. Enroll a New User

```bash
python enroll_newuser.py
```

### 3. Analyze & Visualize

```bash
# FE similarity heatmap
python test_fes_similarity.py

# Legit vs replay score distribution
python generate_score_distribution.py

# FE evaluation from server results
python FE_EVALUATION_TOOLS.py
```

### 4. Trust Network Analysis

```bash
# Full Erdős–Rényi trials (300 networks)
python RDF.py

# Trust score distribution for 30-node / p=0.3
python generate_trust_distribution_graph.py

# Migrate RDF profiles into network subfolders
python migrate_to_networks.py
```

---

## File-by-File Reference

### 🔹 Core Face Recognition

| File | Purpose |
|------|---------|
| **`CLIENT.py`** | Real-time face capture and authentication client. Captures webcam image, detects faces, extracts LBP + 30 disposable-FE vectors, compares locally against `db.json`, and sends all vectors with a signed token to the server. Saves returned RDF profile as `<user>_profile.ttl`. Plots per-FE similarity results. |
| **`server.py`** | Socket server on port 5002. Validates SHA-256 tokens, matches incoming feature vectors against `db.json` per FE index, returns grant/deny results, saves received vectors to `received_vectors/` for audit, and sends the authenticated user's RDF profile. Uses `RDF.py` for RDF integration. |
| **`feature_extractor.py`** | Loads the GA-evolved disposable feature extractors from `disposable FEs.txt` (each FE = 24 patch coordinates, 24 thresholds, radius). `extract_feature_vector()` preprocesses the face (resize 128×128, CLAHE, blur), computes a 3-value descriptor per patch (mean, std, gradient mean), and L2-normalizes. `extract_feature_vector_simple()` is the legacy 24-value version. |
| **`enroll_newuser.py`** | Interactive enrollment script. Prompts for user ID, network selection, captures face via webcam, extracts vectors for ALL 30 FEs, saves to `db.json`, adds the user to `networks.json`, generates their RDF profile, and regenerates friend links for all existing network members. |
| **`rebuild.py`** | Rebuilds `db.json` from captured images in `captured_images/`. Extracts user ID from filenames, processes all 30 FEs per image, and writes a fresh database with N users × 30 FEs. ⚠️ **Destructive overwrite** — see [Known Issues](#known-issues--limitations). |
| **`clean_db.py`** | ⚠️ **BROKEN** — attempts to filter entries whose `feature_vector` has length 60, but the actual schema uses `feature_vectors` dict with 24-value vectors. Will crash with `KeyError`. See [Known Issues](#known-issues--limitations). |
| **`utils.py`** | Shared helpers: SHA-256 token generation, timestamp formatting, base64 image encode/decode, JSON db load/save, sleep utility. |
| **`generate_coord.py`** | Face detection support tool. Opens webcam, detects faces with Haar cascades, saves cropped face to `captured_images/face.jpg` and face coordinates to `captured_images/coord.txt`. |
| **`coord.txt`** | Face bounding-box coordinates written by `CLIENT.py` after detection. |

### 🔹 Replay Attack Testing

| File | Purpose |
|------|---------|
| **`Replay_simulator.py`** | Sends stored feature vectors from `db.json` to the server as if they were freshly captured, simulating a replay attack. Supports `--user` filter and `--delay`. Calls the server with a freshly generated token timed to the current second. |
| **`Replay _ simulator.py`** | Duplicate of `Replay_simulator.py` with a space in the filename (same content). |

### 🔹 Evaluation & Visualization

| File | Purpose |
|------|---------|
| **`FE_EVALUATION_TOOLS.py`** | Loads `eval_results.json` from the server, prints summary stats (granted count, average similarity), and plots similarity bar charts per FE plus grant/deny decision counts. |
| **`test_fes_similarity.py`** | Loads a test face image, extracts LBP + all disposable FE vectors, computes a pairwise cosine-similarity matrix, and saves an annotated heatmap to `similarity_heatmap_disposable.png`. |
| **`generate_score_distribution.py`** | For each enrolled user, computes legit scores (same FE on perturbed versions of the same image) and replay scores (different FEs on the same image). Generates `similarity_score_distribution.png` and the zoomed view with threshold line at 0.85. |
| **`eval_results.json`** | Server results from the last authentication attempt: per-FE status, matched user, and cosine similarity. |

### 🔹 Trust Network Analysis (RDF/WebID)

| File | Purpose |
|------|---------|
| **`RDF.py`** | Core trust-network library. Generates Erdős–Rényi networks, decorates nodes with random attributes (accuracy/speed/reliability/tasks), implements the multi-factor `overall()` ranking (35% centrality + 23% core + 15% avg perf + 9% min perf + 7% assortativity + 6% degree + 4% degree assortativity), runs 300-network trials, and provides RDF/WebID export/import functions (`make_rdf_for`, `write_network_to_rdfs`, `read_in_a_network`). |
| **`network4.py`** | Identical copy of `RDF.py` (the unlocked "working" version). |
| **`generate_trust_distribution_graph.py`** | Imports ranking functions from `RDF.py`, generates a specific 30-node network with p=0.3, computes trust scores, and produces two graphs: `trust_score_distribution_30nodes_p0.3.png` (histogram) and `individual_trust_scores_30nodes_p0.3.png` (bar chart with node IDs). ⚠️ Uses hardcoded display values (min=0.12, max=0.89, mean=0.505, std=0.18) for the statistics text rather than the actual computed values. |
| **`migrate_to_networks.py`** | One-time migration script. Moves existing `.ttl` files from `rdf_profiles/` root into `rdf_profiles/default/`, regenerates each user's profile with `foaf:knows` links to all other default-network members, and ensures `networks.json` lists everyone in "default". Does not modify `db.json`. |
| **`networks.json`** | Registry of all networks and their member user IDs. Example: `{"default": ["Chris", "isaiahfr", ...], "001": ["choice", "cd", ...], "003": ["Sharon"]}`. |
| **`rdf_profiles/`** | Directory structure: `rdf_profiles/<network_name>/<User>.ttl`. Each `.ttl` is a Turtle-format WebID profile with `accuracy`, `speed`, `reliability`, `tasks`, and `foaf:knows` friend links. |

### 🔹 Data Files

| File | Purpose |
|------|---------|
| **`db.json`** | Face feature database. A list of user entries, each with `user_id`, `feature_vector` (legacy FE-0 only), and `feature_vectors` (dict: `"0"`–`"29"` → 24-value vectors). Currently has 17 users. |
| **`disposable FEs.txt`** | GA-evolved feature extractor parameters. Each FE block contains 24 x-coords, 24 y-coords, 24 thresholds, and 2 radius values (rw, rh). Parsed by `feature_extractor.py`. |
| **`used_tokens.json`** | Log of previously used authentication tokens (user_id:timestamp:hash). |
| **`received_vectors/`** | Audit trail of every feature vector received by the server, stored as `user_<id>_fe<index>_<timestamp>.json`. |
| **`captured_images/`** | Captured face images from enrollment and client sessions, named `<user_id>_<timestamp>.png`. |

### 🔹 RDF WebID Profiles

| File | Purpose |
|------|---------|
| **`<user>_profile.ttl`** (e.g., `Chris_profile.ttl`, `Sharon_profile.ttl`, `aprayer_profile.ttl`) | Client-received RDF profiles stored at the project root after successful authentication, showing the user's WebID data that the server sent back. |
| **`rdf_profiles/default/`** | Trust-network profiles for the default network (Chris, Mom, Timbo, etc.). |
| **`rdf_profiles/001/`** | Profiles for the "001" network (aprayer, baldy, cd, choice). |
| **`rdf_profiles/003/`** | Profiles for the "003" network (Sharon). |

### 🔹 Generated Output Images

| File | What It Shows |
|------|---------------|
| **`similarity_heatmap_disposable.png`** | Heatmap of cosine similarity between all 30 disposable FEs on a test face. |
| **`similarity_heatmap_readable.png`** | Human-readable version of the same heatmap. |
| **`similarity_score_distribution.png`** | Overlaid histograms of legit vs replay-attack similarity scores with threshold at 0.85. |
| **`similarity_score_distribution_zoomed.png`** | Zoomed view of legit scores (0.95–1.0 range). |
| **`disposable_fes_similarity_heatmap.png`** | Same as `similarity_heatmap_disposable.png`. |
| **`trust_score_distribution_30nodes_p0.3.png`** | Histogram of trust scores for 30-node network with p=0.3. |
| **`individual_trust_scores_30nodes_p0.3.png`** | Sorted bar chart of individual node trust scores for the same network. |

---

## Database Schema (`db.json`)

```json
[
  {
    "user_id": "Chris",
    "feature_vector": [0.0, 0.5, ...],          // Legacy: FE-0 only (24 values)
    "feature_vectors": {
      "0":  [0.1, 0.2, ...],                    // FE 0 vector (24 values)
      "1":  [0.3, 0.4, ...],                    // FE 1
      ...
      "29": [0.9, 0.8, ...]                     // FE 29
    }
  },
  ...
]
```

**Vector length:** 24 (legacy simple extractor) or 72 (enhanced extractor with 3 values per patch). The server's `match_user()` checks `len(fv) == len(db_fv)` before computing similarity.

---

## RDF Profile Structure (`*.ttl`)

```turtle
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <http://ncat.edu/custom/> .

<http://chris.test> a foaf:Person ;
    ns1:accuracy 3.94e-01 ;
    ns1:reliability 4.02e-02 ;
    ns1:speed 1.36e-01 ;
    ns1:tasks "D", "H" ;
    foaf:knows <http://del.test/webid.ttl>,
        <http://delete.test/webid.ttl> ;
    foaf:name "Chris" .
```

Each profile contains:
- **Performance attributes:** `accuracy`, `speed`, `reliability` (0–1 range)
- **Tasks:** 2–5 tasks from A–I (targets are B, D, F)
- **Friends:** `foaf:knows` links to all other members of the same network

---

## Networks Registry (`networks.json`)

```json
{
  "default": ["Chris", "isaiahfr", "Mom", "Timbo", "rdftest", "rdftest2", "delete", "delete2", "del", "rdfupdate", "elted"],
  "001": ["choice", "cd", "aprayer", "baldy"],
  "003": ["Sharon"]
}
```

The server looks up a matched user's network via `find_user_network()` and serves their RDF profile from `rdf_profiles/<network>/<user>.ttl`.

---

## Workflow Guide

### Enrolling a New User

```
python enroll_newuser.py
```
1. Enter a user ID (e.g., `Mom`)
2. Select or create a network (default / 001 / 003, etc.)
3. Press SPACE to capture your face
4. All 30 FE vectors are extracted and saved to `db.json`
5. User is added to `networks.json` under the selected network
6. An RDF WebID profile is generated at `rdf_profiles/<network>/Mom.ttl`
7. All existing network members' profiles are regenerated to include `foaf:knows` links to the new user

### Authenticating

```
python CLIENT.py
```
1. Webcam opens; press SPACE to capture
2. Faces are detected via Haar cascades; small faces are skipped
3. For each face: LBP vector + 30 FE vectors are extracted
4. Local matching runs first (prints per-FE results)
5. All vectors + token are sent to the server
6. Server validates token, matches against `db.json`, returns per-FE results
7. If any FE matches ≥ 0.85 similarity → final decision = `granted`
8. On grant, server sends the user's RDF profile; client saves it as `<User>_profile.ttl`
9. A bar chart of per-FE similarity is displayed (green = granted, red = denied)

### Testing Replay Attacks

```
python Replay_simulator.py --user Chris --delay 1
```
Sends the stored feature vectors for Chris directly to the server, as if a photo of Chris were being presented to the camera.

### Rebuilding the Database

```
python rebuild.py
```
Scans `captured_images/` for files like `Mom_1778601699.png`, extracts the user ID from the filename, and regenerates all 30 FEs per image into a fresh `db.json`.

### Trust Network Analysis

```
python RDF.py               # Full 300-network trial
python generate_trust_distribution_graph.py   # Specific 30-node / p=0.3 analysis
```

---

## Security Notes

- **Secret key:** `"secret_key"` in `CLIENT.py` and `server.py` must match. This is for development only — do not use in production.
- **Replay protection:** Tokens are SHA-256 of `user_id:timestamp:secret_key:fvs`. However, `server.py` does **not** check `used_tokens.json`, so the same token can be reused within the same second. This is a known gap.
- **Threshold:** Cosine similarity ≥ 0.85 grants access.
- **RDF profiles:** Performance attributes (`accuracy`, `speed`, `reliability`) are **randomly generated** at enrollment time — they are not measured from the user's actual behavior.

---

## Known Issues / Limitations

1. **`clean_db.py` is broken.** It references `entry["feature_vector"]` (a single vector) but the current DB uses `entry["feature_vectors"]` (a dict of 30 vectors). It also expects length 60, but actual vectors are length 24 (legacy) or 72 (enhanced). Running it will raise `KeyError`.

2. **`rebuild.py` runs but has serious side effects.** It works mechanically (30 FEs match `MAX_FE_INDEX = 29`, and all current `captured_images/` filenames parse correctly), but:
   - **Changes vector dimension from 24 → 72.** It uses the enhanced `extract_feature_vector()` (24 patches × 3 descriptors = 72 values), while the current `db.json` stores 24-value legacy vectors. After a rebuild, every entry becomes 72-length.
   - **Drops the `feature_vector` legacy field.** Rebuilt entries only have `feature_vectors`. This breaks `CLIENT.py`'s LBP local matching (`fe_index=None` → looks up `entry["feature_vector"]`), which will return "no match" for everyone.
   - **Destructive overwrite — no merge.** It replaces the entire `db.json` with only users who have images in `captured_images/`. Any enrolled user whose image was deleted is lost.
   - **Multi-image users lose data.** If a user has multiple captures (e.g., `Chris_1.png` and `Chris_2.png`), only the last processed image's vectors survive.
   - **Adds unexpected users.** `captured_images/` contains `Alan powell_1779154075.png`, but there is no "Alan powell" entry in `db.json` or `networks.json`. After a rebuild, "Alan powell" becomes a registered user even though they were never properly enrolled.
   - **Recommendation:** Back up `db.json` before running, and be aware the LBP local-matching path in `CLIENT.py` will stop returning results afterward.

3. **`network4.py` is a duplicate** of `RDF.py`. Keep them in sync or remove one.

4. **`Replay _ simulator.py` (with space)** is a duplicate of `Replay_simulator.py` (no space). Both exist in the repo.

5. **`generate_trust_distribution_graph.py`**  the graph is illustrative, not precise.

6. **No token replay protection** — `used_tokens.json` is not consulted by `server.py` during authentication.

7. **`generate_score_distribution.py`** compares *feature vectors from different FEs* as a proxy for replay attacks; it does not simulate photo-replay against the same FE.

8. **Enrollment captures the entire frame** as the face (`face = gray`) rather than cropping to the detected face, which may reduce matching accuracy.

