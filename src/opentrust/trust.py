"""
PageRank-style trust score propagation.

Each identity's score is determined by the scores of those who endorse it,
weighted by the endorsement weight. Damping factor d=0.85 (standard PageRank).
"""
from .models import TrustGraph

DAMPING = 0.85
ITERATIONS = 100
CONVERGENCE_THRESHOLD = 1e-6


def compute_trust_scores(graph: TrustGraph) -> dict[str, float]:
    """Return a mapping of identity_id -> trust score in [0, 1]."""
    ids = list(graph.identities.keys())
    n = len(ids)
    if n == 0:
        return {}

    # Initialize uniform scores
    scores: dict[str, float] = {id_: 1.0 / n for id_ in ids}

    # Precompute outgoing weight sums per endorser
    out_weight: dict[str, float] = {id_: 0.0 for id_ in ids}
    for e in graph.endorsements:
        out_weight[e.endorser_id] += e.weight

    for _ in range(ITERATIONS):
        new_scores: dict[str, float] = {}
        for id_ in ids:
            incoming = sum(
                scores[e.endorser_id] * e.weight / out_weight[e.endorser_id]
                for e in graph.endorsements
                if e.endorsee_id == id_ and out_weight[e.endorser_id] > 0
            )
            new_scores[id_] = (1 - DAMPING) / n + DAMPING * incoming

        # Check convergence
        delta = sum(abs(new_scores[id_] - scores[id_]) for id_ in ids)
        scores = new_scores
        if delta < CONVERGENCE_THRESHOLD:
            break

    # Normalize to [0, 1]
    max_score = max(scores.values()) or 1.0
    return {id_: round(s / max_score, 6) for id_, s in scores.items()}
