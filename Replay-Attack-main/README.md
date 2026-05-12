Replay-Attack Resistant Face Recognition System

A modular client–server face recognition system designed to perform secure user authentication while detecting replay attacks (e.g., photos or videos presented to the camera). The project includes real-time recognition, enrollment, multiple feature extractors, database management, and tools for evaluating extractor performance.

Key Features
🔹 1. Client–Server Architecture

CLIENT.py captures face images, extracts features, and sends them to the server.

server.py performs feature matching, validation, and returns authentication results.

Modular design allows future upgrade to HTTP/Flask API.

🔹 2. Modular Feature Extraction Framework

Supports multiple facial feature extractors (up to 30+).

feature_extractor.py handles extractor loading and feature vector generation.

Evaluation utilities:

FE_EVALUATION_TOOLS.py

test_fes_similarity.py

Includes similarity heatmaps for comparing extractor performance.

🔹 3. User Enrollment & Database Management

enroll_newuser.py for adding new users.

db.json stores user feature vectors in a simple, lightweight format.

Maintenance tools:

clean_db.py – cleanup unused entries

rebuild.py – rebuild or regenerate the feature database

utils.py – shared helper functions

🔹 4. Replay Attack Simulation & Security Testing

Replay_simulator.py simulates photo/video replay attacks.

Used to verify system robustness and ensure real-time face spoofing detection.

Evaluation metrics stored in eval_results.json.

🔹 5. Supporting Tools

generate_coord.py and coord.txt for patch/grid coordinate generation.

disposable FEs.txt, used_tokens.json for extractor management.

Heatmaps included:

similarity_heatmap_readable.png

disposable_fes_similarity_heatmap.png

Project Structure
├── CLIENT.py
├── server.py
├── feature_extractor.py
├── FE_EVALUATION_TOOLS.py
├── Replay_simulator.py
├── enroll_newuser.py
├── clean_db.py
├── rebuild.py
├── utils.py
├── db.json
├── coord.txt
├── generate_coord.py
├── disposable FEs.txt
├── used_tokens.json
├── similarity_heatmap_readable.png
├── disposable_fes_similarity_heatmap.png
├── eval_results.json
└── README.md

How It Works (High-Level Flow)

User stands in front of the camera.

CLIENT.py captures the face and extracts feature vectors.

Features are sent to the server.

server.py calculates similarity with stored vectors in db.json.

Server returns match / no-match.

Replay simulator can be used to test if system correctly rejects spoof attacks.

Use Cases

Secure access control

Anti-spoofing research

Real-time face verification

Feature extractor evaluation and benchmarking

Future Improvements

Replace socket communication with HTTP/Flask API

Integrate deep learning extractors (FaceNet, ArcFace)

Add liveness detection module

Move from JSON to SQLite database
