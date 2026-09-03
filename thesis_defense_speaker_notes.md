# Thesis Defense Speaker Notes
## A Trust-aware, Biometrically-Secured Network Using Decentralized Identity Protocols and the Analytical Hierarchal Process for Collaboration

**Speaker:** Christopher Parham  
**Advisor:** Dr. Joseph Shelton  
**Committee:** Dr. Muhammad Rais, Dr. Michael Reynolds  
**Venue:** Virginia State University, Department of Computer Science  
**Date:** 2026

---

## Slide 1: Title Slide
**Visual:** Full thesis title, author name, advisor, committee members, university logo/department

**Speaking Notes:**
"Good [morning/afternoon], Dr. Shelton, Dr. Rais, Dr. Reynolds. Thank you for being here today. My name is Christopher Parham, and I'm pleased to present my master's thesis defense. The title of my thesis is 'A Trust-aware, Biometrically-Secured Network Using Decentralized Identity Protocols and the Analytical Hierarchal Process for Collaboration.' I've developed this work under the guidance of my advisor, Dr. Joseph Shelton, with committee members Dr. Muhammad Rais and Dr. Michael Reynolds. Today I'll walk you through the problem I addressed, my proposed solution, the implementation, and the results I obtained."

**Key Emphases:** 
- Three core components: decentralized identity, trust computation, biometrics
- Human-centered approach to security

---

## Slide 2: Presentation Outline
**Visual:** Two-column layout showing Problem/Background, Solution, Implementation, Results

**Speaking Notes:**
"Today's presentation is structured into four main sections. First, I'll discuss the problem statement and motivation - why centralized systems fail and why human factors matter in cybersecurity. Then, I'll present my proposed solution, which combines three innovations: decentralized identity through WebID, trust-based access control using the Analytic Hierarchy Process, and disposable biometric authentication. Next, I'll walk through the system architecture and implementation details. Finally, I'll share the experimental results, discuss key findings, and outline future work."

**Timing Note:** (30 seconds)

---

## Slide 3: Problem Statement & Motivation
**Visual:** Three highlight boxes - Centralized Failures, Human Factors, Research Gap

**Speaking Notes:**
"Let me start with the motivation for this work. Centralized systems remain a critical vulnerability. In 2021, Twitch suffered a major breach due to a server configuration error that exposed source code and user data - a classic single point of failure. Similarly, Target's 2013 breach compromised 40 million customer records stored in a central database.

Beyond infrastructure failures, human factors present ongoing challenges. Passwords can be forgotten, guessed, or stolen. Physical tokens like keycards can be lost or duplicated. Even biometrics, while more secure, have a fundamental flaw: they cannot be changed if compromised.

This brings me to the research gap. No existing system integrates three essential elements: decentralized identity control, dynamic trust-based access control, and privacy-preserving biometric authentication. My thesis addresses this gap."

**Key Emphases:**
- Single point of failure concept
- Irrevocability of biometrics
- Novelty of integrated approach

**Potential Questions:**
- "Why not just use blockchain for everything?" (Complexity, scalability)
- "What makes your approach different from existing DID solutions?" (Trust computation + disposable biometrics)

---

## Slide 4: Solution Overview - Three Core Innovations
**Visual:** Three highlight boxes - WebID, Trust/AHP, Disposable Biometrics

**Speaking Notes:**
"My solution consists of three integrated innovations. 

First, decentralized identity through WebID. Each user operates their own personal server hosting an RDF-based FOAF profile, eliminating the need for a central authority. Users have complete control over their identity data.

Second, trust and task suitability computation using the Analytic Hierarchy Process. I employ betweenness and eigenvector centrality metrics to calculate a geometric mean trustworthiness score. This enables organic coalition formation based on network position.

Third, disposable biometric authentication using Local Binary Patterns combined with Genetic Evolutionary Feature Extraction. Feature extractors are generated for one-time use and then discarded, preventing replay attacks and preserving privacy."

**Key Emphases:**
- "Self-sovereign identity"
- "Organic coalition formation"
- "One-time use" biometrics

---

## Slide 5: WebID & RDF FOAF Profiles
**Visual:** Two-column layout with architecture details and example RDF code

**Speaking Notes:**
"WebID forms the foundation of my system. Each user operates a personal server containing their RDF profile using the FOAF - Friend of a Friend - ontology. This profile includes the user's name, performance attributes like accuracy and reliability, assigned tasks, and social connections through foaf:knows relationships.

The example on the right shows Sharon's RDF profile. You can see her performance metrics and assigned tasks C, H, and I. These profiles are semantically structured, making them machine-readable while maintaining human comprehension.

Importantly, the system employs a hierarchical need-to-know model. Information visibility is limited to the network level - only essential data is exposed for collaboration, minimizing unnecessary data exposure even within the decentralized structure."

**Key Emphases:**
- Semantic web standards
- No central authority
- Hierarchical visibility control

**Potential Questions:**
- "How do you handle profile discovery without a central registry?" (WebID URIs, foaf:knows traversal)
- "What prevents a malicious user from creating fake profiles?" (Biometric authentication requirement)

---

## Slide 6: Trustworthiness Computation
**Visual:** Three boxes - Centrality Metrics, Trust Formula, Trust Tiers

**Speaking Notes:**
"Trust computation is central to my access control mechanism. I use two complementary centrality metrics from network analysis.

Betweenness centrality measures how often a node lies on the shortest paths between other nodes. A node with high betweenness acts as a gatekeeper in the network, controlling information flow - thus highly trustworthy.

Eigenvector centrality addresses qualitative characteristics. A node has high eigenvector centrality not just from having many connections, but from being connected to other influential nodes. This captures the 'birds of a feather' effect - trust through association.

I combine these using the geometric mean: G(n) equals the square root of BC(n) times EC(n). This produces trust scores that I categorize into three tiers: high trust at 0.7 or above, moderate trust between 0.4 and 0.7, and low trust below 0.4."

**Key Emphases:**
- Structural importance = trustworthiness
- Both metrics required for robust assessment
- Geometric mean penalizes extreme imbalance

**Potential Questions:**
- "Why geometric mean instead of arithmetic?" (Geometric mean penalizes extreme imbalance)
- "How are these metrics normalized?" (Min-max scaling to [0,1])

---

## Slide 7: Disposable Biometric Authentication
**Visual:** Two-column layout with LBP/GEFE details and key innovation callout

**Speaking Notes:**
"Now let me explain the biometric authentication mechanism, which I believe is the most innovative aspect of this work.

I use Local Binary Patterns for feature extraction. LBP compares each pixel to its eight neighbors, creating a binary code that captures local texture patterns. This produces a 256-bin histogram representing facial characteristics.

However, standard LBP has limitations. To enhance it, I employ Genetic Evolutionary Feature Extraction. GEFE uses genetic algorithms to evolve optimal LBP regions. Instead of fixed rectangular grids, it allows variable-sized, overlapping regions. The fitness function is recognition accuracy - the algorithm learns which facial regions are most discriminative.

The key innovation here is disposability. Feature extractors are generated fresh for each authentication session using GEFE, then immediately discarded. Session-specific feature vectors are never stored. This means biometric templates cannot be stolen, reused, or reconstructed."

**Key Emphases:**
- LBP captures texture, not just geometry
- GEFE optimizes feature regions
- "One-time use" is the critical security property

**Potential Questions:**
- "How long does feature extraction take?" (Depends on implementation, but goal is real-time)
- "What if the camera quality is poor?" (Adaptive thresholding suggested)

---

## Slide 8: Replay Attack Mitigation
**Visual:** Attack scenario, why replay fails, experimental results

**Speaking Notes:**
"Replay attacks are a major threat to biometric systems. An attacker might intercept transmitted feature vectors and replay them in a future session. My system is specifically designed to defeat this attack vector.

There are four reasons replay attacks fail in my system. First, each session uses different GEFE configurations, so feature extractors are session-specific. Second, this creates dimensional incompatibility - replayed vectors won't match stored enrollment vectors. Third, SHA-256 token validation catches any tampered payloads immediately. Fourth, the voting strategy across 30 extractors means an attacker must defeat all extractors simultaneously.

My experimental results confirm this. Across 7,395 replayed feature vectors, not a single one achieved the 0.85 similarity threshold. This demonstrates perfect resistance to replay attacks while maintaining 100% authentication for legitimate users."

**Key Emphases:**
- Multi-layered defense
- Session-specific randomness
- Quantitative results (7,395 vectors tested)

**Potential Questions:**
- "What if the attacker captures the extractor configuration too?" (Extractor is ephemeral, not transmitted)
- "Could machine learning break this?" (Theoretically possible but practically infeasible given session randomness)

---

## Slide 9: System Architecture
**Visual:** Three-column layout showing Enrollment, Client, Server components

**Speaking Notes:**
"Let me walk through the system architecture. The system has three primary components.

The Enrollment Module captures a user's facial image, extracts 30 feature vectors using disposable extractors, generates their RDF profile with random performance attributes and tasks, and stores everything in the databases. When a user joins an existing network, FOAF relationships are automatically created with all current members.

The Client Authentication component captures a live image, extracts features using the same disposable method, performs local similarity checking against the database, encrypts the vectors with SHA-256, and transmits them via TCP socket.

The Server Verification module receives the connection in a separate thread, decrypts and validates the token, performs independent matching on all vectors, applies the voting strategy, and returns the user's RDF profile upon successful authentication."

**Key Emphases:**
- Modular design
- Two-tier verification (client + server)
- Threaded server for concurrency

---

## Slide 10: Implementation Details
**Visual:** Two-column layout - Technology Stack and Authentication Flow

**Speaking Notes:**
"The implementation uses Python with several key libraries. Face detection employs Haar Cascades. Feature extraction uses LBP with radius 8 and 256 histogram bins. Cosine similarity with a 0.85 threshold determines matches. NetworkX handles centrality computations. Communication occurs over TCP sockets with JSON payloads, and the threaded server handles multiple concurrent clients.

The authentication flow proceeds in nine steps: image capture, feature extraction across 30 extractors, local similarity checking, encryption with SHA-256 token, transmission to server, server decryption and validation, independent matching on each vector, voting across all extractors, and finally retrieval of the RDF profile upon success."

**Key Emphases:**
- Practical technology choices
- End-to-end flow clarity
- Security at each step

---

## Slide 11: Authentication Results
**Visual:** Three highlight boxes - Enrollment, Legitimate Auth, Replay Attack Resistance

**Speaking Notes:**
"I tested the system with 17 users across three subnetworks. Each user had 30 feature vectors extracted during enrollment.

For legitimate authentication, the results were perfect: 100% success rate. All 17 users were successfully authenticated with an average cosine similarity of 0.998. Individual extractors occasionally scored below 0.85 due to lighting or position variations, but at least one extractor always matched above threshold. Importantly, client and server decisions were identical in every case, confirming algorithm consistency.

For replay attacks, I tested 7,395 vectors representing intercepted biometric data from previous sessions. Every single one failed to authenticate. The average similarity for replayed vectors was effectively zero. This validates that disposable extractors provide robust replay resistance."

**Key Emphases:**
- 100% legitimate success
- 0% replay success
- Sample size significance (7,395 tests)

**Potential Questions:**
- "What caused the occasional legitimate failures?" (Lighting, position - addressed by multiple extractors)
- "Did you test with different cameras/lighting?" (Suggested future work)

---

## Slide 12: Trust Experiment Results
**Visual:** Three boxes - Fully Connected Limitation, Erdős–Rényi Results, Validation

**Speaking Notes:**
"The trust computation results reveal both a limitation and validation of my model.

In my implemented system, automatic FOAF connections create fully connected subnetworks. In this configuration, all betweenness centrality values become zero because there are equal-length paths through the network. The geometric mean with zero produces a trust score of zero for all users - the model collapses.

To validate the trust model under realistic conditions, I conducted a follow-up experiment using Erdős–Rényi random networks. With 30 nodes and edge probability 0.3, these sparse networks produced meaningful centrality variation. Trust scores ranged from 0.12 to 0.89 with a standard deviation of 0.18.

This confirms the model works as intended in networks with selective friendships - exactly the real-world scenario. The limitation in fully connected graphs is solvable through friendship caps or weighted relationship edges."

**Key Emphases:**
- Honest reporting of limitations
- Distinction between implementation and validation
- Real-world applicability confirmed

**Potential Questions:**
- "Why not use Erdős–Rényi directly?" (Real networks aren't random; need realistic FOAF structure)
- "How would weighted edges help?" (Relationships have different strengths)

---

## Slide 13: Key Findings & Contributions
**Visual:** Three validation status boxes (2 green checkmarks, 1 orange warning), plus improvement areas

**Speaking Notes:**
"Let me summarize the key findings from my research.

Hypothesis 1 - Disposable biometric authentication - is fully validated. The system achieves 100% authentication success for legitimate users and 0% success for replay attacks. The combination of LBP and GEFE with session-specific extractors provides robust security.

Hypothesis 2 - Trust computation - is partially validated. The model produces meaningful differentiation in sparse networks but requires adjustment for fully connected topologies. This is a known limitation that can be addressed.

Hypothesis 3 - The integrated framework - is validated. Combining decentralized identity, trust-based access, and disposable biometrics creates a cohesive, secure collaboration platform.

Areas for improvement include implementing adaptive thresholding for poor lighting conditions, deriving performance attributes from actual task history rather than random assignment, and moving from binary to weighted FOAF relationships."

**Key Emphases:**
- Scientific honesty about limitations
- 2 out of 3 hypotheses fully validated
- Clear path forward

---

## Slide 14: Privacy & Ethical Implications
**Visual:** Three highlight boxes - Privacy Advantages, Biometric Concerns, Trust Bias Risk

**Speaking Notes:**
"Privacy and ethics are critical considerations in any identity system.

The decentralized architecture provides significant privacy advantages. Without central data aggregation, there's no single repository for mass scraping. Each user's RDF profile and FOAF relationships remain under their direct control. The need-to-know model minimizes unnecessary exposure even within networks.

However, biometric concerns remain. Even with disposable templates, facial image capture involves sensitive data. Users must trust that templates are actually discarded after use - this requires system transparency and auditability.

An important ethical consideration is trust bias. New users naturally have lower centrality and thus lower trust scores, potentially creating structural discrimination. I recommend implementing transparency in trust computation, an appeal system for scores, and safeguards against centrality-based exclusion."

**Key Emphases:**
- Privacy by design
- Residual biometric risks
- Fairness and transparency

**Potential Questions:**
- "How do you verify template destruction?" (Cryptographic attestation, audit logs)
- "Can users see their trust score calculation?" (Transparency requirement)

---

## Slide 15: Conclusion & Future Work
**Visual:** Three highlight boxes - Summary, Future Extensions, Impact

**Speaking Notes:**
"In conclusion, this thesis presents a novel framework that integrates three critical capabilities for secure decentralized collaboration: WebID-based self-sovereign identity, trust-based access control using network centrality, and privacy-preserving disposable biometric authentication.

Future work includes extending to multiple biometric modalities - fingerprint, voice, iris, keystroke dynamics - all using the same disposable extraction model. Blockchain integration could provide immutable audit trails for trust scores and authentication events. Dynamic reputation derived from actual task execution would replace the current random attributes. Adaptive trust models with weighted edges and temporal decay would better reflect real-world relationships. Finally, compliance with emerging Self-Sovereign Identity standards would enhance interoperability.

The impact of this work is enabling next-generation collaborative platforms that prioritize user autonomy, trust-based cooperation, and privacy-preserving security in federated environments - from remote teams to secure social platforms."

**Key Emphases:**
- Interdisciplinary contribution (networks + security + biometrics)
- Practical deployability
- Vision for future systems

---

## Slide 16: Q&A
**Visual:** Large "Questions?" text, contact information

**Speaking Notes:**
"Thank you for your attention. I'm happy to answer any questions you may have about the methodology, results, or future directions of this work."

**Action:** Invite questions from committee, be prepared to elaborate on any technical aspect of the research.

---

## Anticipated Questions & Suggested Responses

### Technical Questions

**Q: How does your system handle network partitions or offline users?**
A: Good question. The current implementation assumes connected networks. For partitions, the federated nature means each personal server remains operational locally. FOAF relationships could be cached and synchronized upon reconnection. This is a natural extension for distributed systems work.

**Q: What prevents a Sybil attack where a user creates multiple fake identities?**
A: Biometric enrollment requires physical presence and a live facial capture. Each identity needs a unique biometric trait. While sophisticated spoofing exists, the disposable extractor model makes template reuse across identities extremely difficult. Plus, the trust computation naturally isolates nodes with suspicious centrality patterns.

**Q: Why 30 feature extractors? Did you optimize this number?**
A: The number 30 provides robustness through the voting strategy. More extractors increase resilience but also computational cost. I chose 30 as a practical balance. Future work could optimize this based on desired security levels and performance constraints.

### Methodology Questions

**Q: Why cosine similarity instead of Euclidean distance?**
A: Cosine similarity measures angular distance, which is more robust to illumination variations in facial images. It focuses on the pattern rather than absolute intensity values, making it better suited for LBP histograms.

**Q: How long does the authentication process take end-to-end?**
A: The current Python implementation processes authentication in under 2 seconds. This includes capture, 30 extractor evaluations, and network communication. GPU acceleration and optimized implementations could reduce this significantly.

**Q: Did you compare against existing biometric systems?**
A: The focus was on the disposable extractor concept rather than raw accuracy competition. Standard LBP with persistent templates achieves similar accuracy but with critical security differences. The comparison shows my approach maintains accuracy while adding replay resistance.

### Broader Impact Questions

**Q: What's the real-world deployment path for this technology?**
A: The WebID standards are mature, and biometric APIs are widely available. Deployment could start in controlled environments - corporate networks, government agencies, healthcare systems - where organizations can enforce biometric enrollment. The architectural flexibility allows gradual adoption.

**Q: How does this relate to existing SSI (Self-Sovereign Identity) standards?**
A: This work complements SSI initiatives. My system could integrate with DID (Decentralized Identifier) standards for the identity layer while adding the unique contributions of trust-based access control and disposable biometrics. The RDF profiles align with Verifiable Credentials data models.

---

## Timing Guide

**Total Presentation Time: 15-20 minutes typical for master's defense**

| Slide | Topic | Suggested Time |
|-------|-------|----------------|
| 1 | Title | 0:30 |
| 2 | Outline | 0:30 |
| 3 | Problem Statement | 1:30 |
| 4 | Solution Overview | 1:00 |
| 5 | WebID/RDF | 1:30 |
| 6 | Trust Computation | 1:30 |
| 7 | Biometrics | 1:30 |
| 8 | Replay Attacks | 1:00 |
| 9 | Architecture | 1:00 |
| 10 | Implementation | 1:00 |
| 11 | Auth Results | 1:30 |
| 12 | Trust Results | 1:00 |
| 13 | Key Findings | 1:00 |
| 14 | Privacy/Ethics | 1:00 |
| 15 | Conclusion | 1:00 |
| 16 | Q&A | Remaining time |

**Total Speaking: ~15 minutes**
**Remaining: Q&A period (typically 15-30 minutes)**

---

## Presentation Tips

1. **Practice transitions** - Have clear verbal bridges between sections
2. **Emphasize novelty** - The integration of three distinct innovations is the thesis contribution
3. **Be honest about limitations** - The fully connected network issue shows scientific rigor
4. **Quantify results** - Use specific numbers (100%, 0%, 0.998, 7,395) to reinforce claims
5. **Prepare for deep dives** - Committee may ask about LBP implementation details, NetworkX centrality algorithms, or RDF serialization
6. **Connect to literature** - Reference the papers cited in thesis when appropriate
7. **Show enthusiasm** - This is human-centered security work with real-world impact

---

## Backup Slides (if needed)

The following topics might be requested as additional slides:
- Detailed LBP algorithm pseudo-code
- Genetic algorithm parameters for GEFE
- Network graph visualizations (social graphs, Erdős–Rényi examples)
- RDF profile generation flow
- FOAF relationship lifecycle
- Security logging format examples
- Similarity score distribution histogram
- Centrality metric computation details
- Threading architecture diagram
- Database schema for JSON storage

Good luck with your defense!