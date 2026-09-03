# Implementation: Facial Recognition Authentication System

## 4. System Implementation and Component Interaction

The proposed replay attack detection system is implemented as a distributed authentication architecture comprising three primary software components: the enrollment module (`enroll_newuser.py`), the client authentication module (`CLIENT.py`), and the server verification module (`server.py`). These components interact through a combination of shared file-based storage and TCP socket communication to provide a multi-feature-extractor facial recognition system with semantic web identity integration.

### 4.1 Shared Data Layer

The system relies on a shared data layer that facilitates communication between components through persistent storage. Two primary data stores form the backbone of the system:

**Feature Vector Database (`db.json`):** This file maintains a registry of enrolled users and their corresponding feature vectors. Each user entry contains a unique identifier (`user_id`) and a collection of feature vectors extracted using multiple disposable feature extractors (FEs). The structure supports both legacy single-vector storage (`feature_vector`) and the contemporary multi-vector approach (`feature_vectors`), where each extractor index maps to its corresponding feature vector. This database is written by the enrollment module and read by both the client and server modules during authentication.

**Network Registry (`networks.json`):** This file implements a network-based user organization system, mapping network names to lists of member user identifiers. It enables the formation of distinct user groups, where each user belongs to exactly one network. The file is maintained by the enrollment module and consulted by the server module to resolve user identity and retrieve associated semantic profiles.

**RDF Profile Store (`rdf_profiles/`):** This directory stores semantic WebID profiles in Turtle (`.ttl`) format, organized hierarchically by network name. Each profile encodes user attributes including accuracy, speed, reliability metrics, assigned tasks, and friend relationships with other network members. These profiles serve as a decentralized identity layer, enabling semantic interoperability between system components.

### 4.2 Enrollment Phase: User Registration

The enrollment procedure, implemented in `enroll_newuser.py`, establishes the foundational identity record for each user. The process unfolds in five sequential stages:

**Stage 1 — Network Affiliation:** Upon execution, the enrollment module prompts the user to select or create a network via the `select_network()` function. This function loads the existing network registry from `networks.json`, presents available networks to the user, and handles various input modes including numeric selection, name matching, and network creation. Once a network is selected, the module records the user's membership by appending the user identifier to the appropriate network list through `add_user_to_network()`.

**Stage 2 — Biometric Capture:** The module activates the system webcam via OpenCV's `VideoCapture` interface and displays a live video feed. The user initiates capture by pressing the space bar, at which point the current frame is retrieved as a grayscale image. The captured face image is saved to the `captured_images/` directory with a timestamped filename for audit purposes.

**Stage 3 — Multi-Feature Extraction:** The system loads all available disposable feature extractors through the `load_feature_extractors()` function. For each extractor index, the module invokes `extract_feature_vector()` to compute a feature vector from the captured face image. These vectors are aggregated into a dictionary mapping extractor indices to their corresponding vectors, enabling the system to leverage multiple independent feature representations for improved robustness against replay attacks.

**Stage 4 — Database Persistence:** The extracted feature vectors are stored in the local database (`db.json`). The `load_local_db()` function reads the existing database contents, after which the module either updates an existing user entry (if the user identifier already exists) or appends a new entry. The `save_local_db()` function persists the updated database to disk with formatted JSON indentation.

**Stage 5 — Semantic Profile Generation:** Concurrently with biometric enrollment, the module generates a semantic WebID profile for the newly enrolled user using the RDF (Resource Description Framework) integration. Random attribute values (accuracy, speed, reliability) are generated alongside a variable set of task assignments. Friend relationships are automatically computed as all other members of the same network, excluding the newly enrolled user. The `make_rdf_for()` function serializes this profile to a Turtle-format file within the network-specific subdirectory of `rdf_profiles/`. Critically, when a user joins an existing network with pre-existing members, the `regenerate_network_rdfs()` function updates the profiles of all existing members to include the new user as a friend, thereby maintaining bidirectional friendship consistency across the network.

### 4.3 Authentication Phase: Client-Server Architecture

The authentication process implements a two-tier verification architecture where the client performs preliminary local matching before transmitting feature vectors to the server for authoritative validation.

#### 4.3.1 Client-Side Processing (`CLIENT.py`)

**Biometric Capture and Face Detection:** The client module captures a live facial image using the same webcam interface as the enrollment module. The captured grayscale image is processed through a Haar Cascade classifier (`haarcascade_frontalface_default.xml`) to detect facial regions. Detected face coordinates are saved to `coord.txt` for diagnostic purposes.

**Feature Extraction:** For each detected face region, the client extracts feature vectors using two categories of feature extractors:

1. *Local Binary Pattern (LBP)*: A manual LBP feature vector is computed using the `extract_lbp_feature_vector()` function, which applies uniform LBP with a radius of 1 and 8 sampling points, then computes a normalized histogram over 256 bins.

2. *Disposable Feature Extractors*: The same set of disposable feature extractors used during enrollment is loaded and applied to extract multiple feature vectors per face.

**Local Database Comparison:** Each extracted feature vector is compared against the local copy of `db.json` using cosine similarity as the distance metric, as formalized in Equation (1):

$$\text{sim}(v_1, v_2) = \frac{v_1 \cdot v_2}{\|v_1\| \|v_2\|}$$ (1)

A similarity threshold of 0.85 determines whether a match is considered valid. The `compare_with_local_db()` function iterates through all enrolled users and returns the best matching user identifier along with the corresponding similarity score. For users enrolled with multiple feature vectors, the function retrieves the appropriate vector corresponding to the current feature extractor index.

**Secure Payload Construction and Transmission:** The client constructs a JSON payload containing all extracted feature vectors, each annotated with its corresponding feature extractor index. To ensure data integrity during transmission, the client computes a SHA-256 authentication token as shown in Equation (2):

$$\text{token} = \text{SHA256}(\text{user\_id} : \text{timestamp} : \text{secret\_key} : \text{FV\_string})$$ (2)

where `FV_string` is the concatenated string representation of all feature vectors. This token mechanism prevents tampering with the feature vector data during network transit. The payload, including the token, timestamp, and user identifier, is serialized to JSON and transmitted to the server via a TCP socket connection.

**Communication Protocol:** The client-server communication employs a length-prefixed messaging protocol to handle variable-length JSON payloads:

1. The client establishes a TCP connection to `127.0.0.1:5002`.
2. A 16-byte header containing the total payload length (left-padded with spaces) is transmitted.
3. The full JSON payload follows the header.
4. The client awaits the server's response, receiving up to 8192 bytes.

#### 4.3.2 Server-Side Verification (`server.py`)

**Concurrent Connection Handling:** The server operates as a multithreaded TCP listener bound to `0.0.0.0:5002`. Upon accepting a client connection, it spawns a new thread via `threading.Thread` to handle the request concurrently, enabling simultaneous processing of multiple authentication requests.

**Payload Reception and Token Validation:** The server reconstructs the JSON payload by first reading the 16-byte length header, then receiving data in 4096-byte chunks until the complete payload is assembled. Token validation is performed by recomputing the SHA-256 hash using the received parameters and the pre-shared secret key. If the computed token does not match the received token, the server immediately rejects the request with a "denied" status and "invalid_token" reason, preventing unauthorized or tampered authentication attempts from proceeding.

**Multi-Feature Vector Matching:** For each feature vector in the received payload, the server performs an independent matching operation against the central `db.json` database using the same cosine similarity metric and 0.85 threshold employed by the client. The `match_user()` function retrieves the stored feature vector corresponding to the same feature extractor index used during enrollment, ensuring dimensional compatibility between enrollment and authentication vectors.

**Result Aggregation and Decision Logic:** The server aggregates results from all feature extractors into a JSON response array, where each entry records:

- The feature extractor index (`fe_index`)
- The authentication decision (`status`: "granted" or "denied")
- The matched user identifier (`matched_user`)
- The cosine similarity score (`similarity`)

The system employs an **any-match voting strategy**: authentication is granted if any single feature extractor produces a match equal to or exceeding the 0.85 threshold. This voting scheme leverages the diversity of independent feature extractors to improve overall system robustness — a replay attack that succeeds against one extractor is unlikely to simultaneously fool all others.

**Semantic Profile Retrieval:** Upon successful authentication, the server determines the user's network affiliation by searching `networks.json` through the `find_user_network()` function. It then retrieves the user's RDF WebID profile from the corresponding network subdirectory within `rdf_profiles/`. If the profile exists, its Turtle-format content is included in the response as the `rdf_profile` field, enabling the client to access the authenticated user's semantic identity data.

**Audit Logging:** Each received feature vector is persisted to the `received_vectors/` directory with a filename encoding the user identifier, feature extractor index, and timestamp, providing a comprehensive audit trail for security analysis and system evaluation.

### 4.4 Post-Authentication Client Processing

Upon receiving the server's response, the client module performs two post-processing operations:

1. **Response Persistence:** The complete server response is saved to `eval_results.json` for evaluation and debugging purposes.

2. **Visualization:** A bar chart is generated using Matplotlib, displaying the cosine similarity scores for each feature extractor. Matches exceeding the 0.85 threshold are colored green (granted status) while sub-threshold matches appear red (denied status). A horizontal dashed line marks the decision threshold, providing immediate visual feedback on the authentication outcome.

3. **RDF Profile Storage:** If authentication is granted and the server returns an RDF profile, the client saves this profile to a local file named after the matched user (e.g., `{username}_profile.ttl`), enabling the authenticated user to possess their semantic identity data locally.

### 4.5 Security Considerations

The implementation incorporates several security mechanisms to mitigate replay attacks and ensure data integrity:

**Token-Based Payload Integrity:** The SHA-256 authentication token binds the feature vector data to the timestamp and user identifier using a pre-shared secret key. This construction prevents an attacker from intercepting and modifying the feature vectors in transit, as any alteration would invalidate the token and be detected during server-side validation.

**Multi-Extractor Diversity:** By employing multiple independent feature extractors with different algorithmic bases, the system creates a defense-in-depth mechanism where an attacker must simultaneously defeat all extractors to achieve authentication. The any-match voting strategy further enhances usability by tolerating individual extractor failures.

**Timestamp Integration:** The inclusion of a Unix timestamp in the token provides a basis for replay attack detection. While the current implementation performs timestamp collection, production deployments could extend this by validating timestamp freshness against a configurable window.

### 4.6 Component Interaction Summary

Figure 4.1 illustrates the complete interaction flow between the three system components:

1. **Enrollment → Database:** `enroll_newuser.py` writes feature vectors to `db.json`, network membership to `networks.json`, and RDF profiles to `rdf_profiles/`.

2. **Client → Database (Read):** `CLIENT.py` reads `db.json` for preliminary local matching before server transmission.

3. **Client → Server (Socket):** `CLIENT.py` transmits feature vectors with integrity tokens to `server.py` via TCP socket on port 5002.

4. **Server → Database (Read):** `server.py` reads `db.json` and `networks.json` for authoritative user matching and network resolution.

5. **Server → RDF Store (Read):** `server.py` reads RDF profiles from `rdf_profiles/{network}/` for authenticated users.

6. **Server → Client (Response):** `server.py` returns authentication results and (if granted) the user's RDF profile to the client.

This architecture decouples enrollment from authentication while maintaining a consistent identity framework through shared data structures and standardized feature extraction protocols. The socket-based communication layer provides network transparency, enabling the client and server to operate on different physical machines while the shared file system could be migrated to a centralized database for production deployment.