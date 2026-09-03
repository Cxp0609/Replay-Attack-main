# 3. Network Centrality-Based Trustworthiness Assessment

## 3.1 Introduction

Trustworthiness in a social network can be meaningfully grounded in centrality measures, as individuals who occupy influential positions and control network traffic are generally considered trustworthy. This section develops a notion of trustworthiness based on the geometric mean of two complementary centrality measures: betweenness centrality and eigenvector centrality. The framework follows the methodology of Dowtin et al. (2023), which argues that centrality-based trustworthiness meets the intuitive expectation that structurally important nodes should be considered trustworthy. De Meo et al. (2017) evaluated degree centrality, closeness centrality, betweenness centrality, eigenvector centrality, and PageRank for predicting local reputation and trust based on ratings, finding eigenvector centrality to be the most effective predictor among the standard measures.

## 3.2 Betweenness Centrality

The betweenness centrality of a node \(n\) in a graph \(G\) quantifies the extent to which \(n\) lies on the shortest paths between other pairs of nodes (Freeman, 1977). Formally:

$$ B(n) = \sum_{s \neq n \neq t} \frac{\sigma_{st}(n)}{\sigma_{st}} $$

where \(\sigma_{st}\) is the total number of shortest paths between nodes \(s\) and \(t\), and \(\sigma_{st}(n)\) is the number of those shortest paths that pass through node \(n\).

In the context of trustworthiness, betweenness centrality measures a node's capacity to regulate the flow of information among other nodes in the network. A node with high betweenness centrality acts as a gatekeeper — it controls the communication channels through which information must pass. High betweenness centrality indicates that the node occupies a structurally important position and would therefore be considered highly trustworthy, as its cooperation is essential for efficient network communication.

Certain properties of betweenness centrality warrant attention. A degree-one node (a leaf node connected to the network by a single edge) has betweenness centrality zero, as there can be no shortest paths passing through it without it being an endpoint. For example, in a path graph on four nodes with edges \(\{0, 1\}, \{1, 2\}, \{2, 3\}, \{3, 4\}\), nodes 0 and 4 have betweenness centrality zero while the other nodes have positive values. In a complete graph where every node is directly connected to every other node, all betweenness centralities are zero, as every shortest path is simply the direct edge between the two nodes in question. These properties are discussed further in Section 3.6.

## 3.3 Eigenvector Centrality

Eigenvector centrality addresses the qualitative nature of a node's connections by measuring not only how many connections a node has, but the influence of the nodes to which it is connected. Given the adjacency matrix \(A\) of graph \(G\) with \(N\) nodes, the eigenvector centrality \(x_n\) of node \(n\) is the \(n\)-th component of the principal eigenvector \(x\) satisfying:

$$ A x = \lambda_{\max} x $$

where \(\lambda_{\max}\) is the largest eigenvalue of \(A\). This formulation captures the recursive notion that a node is influential if it is connected to other influential nodes.

As a trustworthiness indicator, eigenvector centrality captures two features of social standing: how many people one knows (the degree component) and whom one knows (the quality-of-connections component). A node with high eigenvector centrality is connected to other highly central nodes, placing it in a position of influence within the network. To have a high eigenvector centrality value, a node must have connections with other influential nodes in the network. This measure captures the intuition that trustworthiness is not merely a function of one's direct connections, but of the broader network context in which those connections exist.

The following alternative centrality measures are excluded from this framework for the reasons stated. Closeness centrality (Bavelas, 1948), defined as the multiplicative inverse of the sum of the lengths of shortest paths from a node to all other nodes, does not reflect the structural topology of the network in a manner conducive to trust assessment — it measures reachability rather than influence or gatekeeping capacity. PageRank is conceptually similar to eigenvector centrality but introduces a damping factor and random surfer model designed for web page ranking rather than social network trust assessment; the two measures produce highly correlated rankings, and eigenvector centrality provides a more theoretically direct foundation. EigenTrust (Kamvar, 2003), designed for peer-to-peer networks, defines trust scores as transitive and computes reputation via the leading eigenvector of a trust matrix derived from download authenticity ratios; this notion is too domain-specific for general social network trustworthiness assessment.

## 3.4 Combined Trustworthiness Score

To derive a unified measure of trustworthiness from the two selected centrality dimensions, we employ the geometric mean of the normalized betweenness centrality and eigenvector centrality values. Let \(x_n\) and \(B_n\) represent the normalized eigenvector centrality and betweenness centrality values of node \(n\), respectively, each scaled to the interval \([0, 1]\). The combined trustworthiness score \(G(n)\) is defined as:

$$ G(n) = \sqrt{x_n \cdot B_n} $$

The geometric mean is selected over alternative aggregation methods for three principal reasons, following the reasoning articulated by the United Nations Development Programme (2019) in its adoption of the geometric mean for the Human Development Index (HDI).

First, with the geometric mean, a low achievement in one dimension is not linearly compensated by a higher achievement in another dimension. In the trustworthiness context, a node with extremely low betweenness centrality (e.g., \(B_n \approx 0\)) cannot offset this deficiency through high eigenvector centrality alone; the resulting score \(G(n)\) remains low, accurately reflecting the node's structural weakness as a gatekeeper.

Second, the geometric mean reduces the level of substitutability between dimensions, ensuring that both centrality measures must contribute meaningfully to the trustworthiness score. This property is particularly important for trust assessment, where both influence (eigenvector centrality) and gatekeeping capacity (betweenness centrality) are essential. A simple arithmetic mean would allow a high score in one dimension to mask a deficiency in the other, which would be inappropriate for trust assessment.

Third, a small decline in one centrality measure has the same proportional impact on \(G(n)\) as a small decline in the other measure, ensuring fair treatment of both dimensions. The geometric mean is concave and symmetric, satisfying the fundamental requirements for a well-behaved aggregation function. The concavity property ensures that the trustworthiness score exhibits diminishing marginal returns — increases in centrality at higher levels contribute less to the combined score than equivalent increases at lower levels.

## 3.5 Application to RDF Social Network Graphs

The centrality-based trustworthiness framework described above is naturally applicable to communities of peers organized through RDF WebID profiles. In such systems, each participant maintains a semantic profile document containing their identity attributes and social connections. These connections are typically expressed through reciprocal `foaf:knows` triples using the Friend of a Friend (FOAF) vocabulary, which defines relationships between people in a machine-readable format. When each participant's profile declares bidirectional knowledge relationships with a subset of other participants, the collection of these profiles implicitly defines the adjacency structure of a social network graph.

The adjacency matrix \(A\) of such a network is constructed as follows. For a network of \(N\) participants, each participant corresponds to a node indexed from 1 to \(N\). An entry \(a_{m,n} = 1\) if the RDF profiles of participants \(m\) and \(n\) contain reciprocal `foaf:knows` relationships, and \(a_{m,n} = 0\) otherwise. The matrix is symmetric by construction, reflecting the reciprocal nature of the friendship relationship.

From this adjacency matrix, the betweenness centrality and eigenvector centrality values for each node can be computed using standard graph analysis algorithms. Betweenness centrality requires enumerating shortest paths between all pairs of nodes, which can be accomplished via the Brandes algorithm (Brandes, 2001) with time complexity \(O(NM)\) for unweighted graphs, where \(N\) is the number of nodes and \(M\) is the number of edges. Eigenvector centrality is computed via the power iteration method, which iteratively multiplies the adjacency matrix by a candidate eigenvector until convergence, with time complexity \(O(N^2)\) per iteration.

The resulting trustworthiness score \(G(n)\) for each participant reflects their structural position in the RDF-defined social network. Participants who bridge otherwise disconnected subgroups (high betweenness centrality) and participants who are connected to other highly central participants (high eigenvector centrality) receive high trustworthiness scores. This score provides a structural trust assessment that is independent of any behavioral history, making it particularly valuable for systems where participants have limited interaction history.

The trustworthiness score could modulate authentication decisions in a tiered manner. Participants with high trustworthiness scores (\(G(n) \geq 0.7\)) may be authenticated with standard verification thresholds. Those with moderate scores (\(0.4 \leq G(n) < 0.7\)) may require elevated thresholds or additional verification factors. Those with low scores (\(G(n) < 0.4\)) may trigger enhanced verification mechanisms. This tiered approach makes the system context-aware, adapting its security posture based on each participant's established position in the social network graph derived from their RDF profiles.

## 3.6 Limitations

The proposed trustworthiness measure based on the geometric mean of betweenness and eigenvector centrality has several limitations that must be acknowledged.

**Complete Graph Problem.** In graphs where every node is directly connected to every other node, all betweenness centralities are zero. If the RDF social network forms a complete or near-complete graph — for instance, if every participant declares a `foaf:knows` relationship with every other participant — then the geometric mean \(G(n) = \sqrt{x_n \cdot B_n}\) collapses to zero for all nodes, rendering the betweenness centrality component meaningless. This situation arises when the friendship policy is overly permissive.

Several strategies can address this limitation. A sparser graph could be achieved through a friendship request and acceptance mechanism, where participants only declare relationships with a subset of the network. Alternatively, a maximum friend cap could limit each participant to a fixed number of connections, creating a bounded-degree graph. Edge weights could also be introduced based on interaction frequency or similarity scores, transforming the binary graph into a weighted graph where betweenness centrality captures not just structural position but interaction intensity.

**Scalability Constraints.** Computing betweenness centrality via the Brandes algorithm has time complexity \(O(NM)\) for unweighted graphs, while eigenvector centrality via power iteration requires \(O(N^2)\) per iteration. For networks with thousands of participants, these computations become non-trivial and may require incremental update algorithms that recalculate centrality scores only for affected nodes when the network topology changes.

**Structural Versus Behavioral Trustworthiness.** The centrality-based trustworthiness measure reflects a node's structural position in the social network rather than its behavioral reputation. While the two concepts are correlated — structurally central nodes tend to behave more reliably to maintain their position — they are not identical. Behavioral reputation could be tracked separately through interaction history, and the two measures could be combined for a more comprehensive trust assessment.

## 3.7 Chapter Summary

This section has presented a framework for assessing trustworthiness in social networks based on the geometric mean of betweenness centrality and eigenvector centrality. The framework draws on established network centrality measures and adapts them to the specific requirements of trust assessment, where both gatekeeping capacity (betweenness centrality) and influence (eigenvector centrality) are essential dimensions. The geometric mean provides a principled aggregation method that prevents high achievement in one dimension from masking low achievement in another.

The framework is particularly well-suited to RDF-based social network graphs constructed from reciprocal `foaf:knows` triples, as the adjacency structure required for centrality computation is directly derivable from the participants' semantic profiles. The resulting trustworthiness scores can be used to inform context-aware authentication decisions, adapting security thresholds based on each participant's structural position in the network.

---

## References

Bavelas, A. (1948). A mathematical model for group structures. *Human Organization*, 7(3), 16-30.

Brandes, U. (2001). A faster algorithm for betweenness centrality. *Journal of Mathematical Sociology*, 25(2), 163-177.

De Meo, P., et al. (2017). A reputation-based framework for trust assessment in social networks. *IEEE Transactions on Computational Social Systems*, 4(3), 115-126.

Dowtin, A., et al. (2023). A notion of trustworthiness based on centrality in a social network. *Proceedings of the International Conference on Social Computing*, 52-62.

Freeman, L. C. (1977). A set of measures of centrality based on betweenness. *Sociometry*, 40(1), 35-41.

Kamvar, S. D., et al. (2003). EigenTrust: Reputation management in P2P networks. *Proceedings of the 12th International World Wide Web Conference*, 640-651.

Newman, M. E. J. (2018). *Networks* (2nd ed.). Oxford University Press.

United Nations Development Programme. (2019). *Human Development Report 2019: Beyond Income, Beyond Averages, Beyond Today*. United Nations.