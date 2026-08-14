import pytest
from fastapi.testclient import TestClient
from opentrust.api import app, graph
from opentrust.models import Endorsement, Identity, TrustGraph
from opentrust.trust import compute_trust_scores


@pytest.fixture(autouse=True)
def reset_graph():
    """Reset the in-memory graph before each test."""
    graph.identities.clear()
    graph.endorsements.clear()
    yield


client = TestClient(app)


# --- Model tests ---

def test_identity_defaults():
    identity = Identity(name="Alice")
    assert identity.id
    assert identity.name == "Alice"


def test_endorsement_weight_bounds():
    with pytest.raises(Exception):
        Endorsement(endorser_id="a", endorsee_id="b", weight=1.5)


def test_trust_graph_self_endorsement():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    with pytest.raises(ValueError, match="Cannot endorse yourself"):
        g.add_endorsement(Endorsement(endorser_id=alice.id, endorsee_id=alice.id))


def test_trust_graph_unknown_endorser():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    with pytest.raises(ValueError, match="not found"):
        g.add_endorsement(Endorsement(endorser_id="unknown", endorsee_id=alice.id))


def test_re_endorsement_updates_existing_edge():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    bob = g.add_identity(Identity(name="Bob"))
    g.add_endorsement(Endorsement(endorser_id=alice.id, endorsee_id=bob.id, weight=0.3))
    g.add_endorsement(Endorsement(endorser_id=alice.id, endorsee_id=bob.id, weight=0.9))
    assert len(g.endorsements) == 1
    assert g.endorsements[0].weight == 0.9


def test_remove_endorsement():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    bob = g.add_identity(Identity(name="Bob"))
    e = g.add_endorsement(Endorsement(endorser_id=alice.id, endorsee_id=bob.id))
    assert g.remove_endorsement(e.id) is True
    assert g.endorsements == []
    assert g.remove_endorsement(e.id) is False


# --- Trust score tests ---

def test_trust_scores_empty_graph():
    assert compute_trust_scores(TrustGraph()) == {}


def test_trust_scores_single_node():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    scores = compute_trust_scores(g)
    assert scores[alice.id] == 1.0


def test_trust_scores_endorsed_node_ranks_higher():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    bob = g.add_identity(Identity(name="Bob"))
    carol = g.add_identity(Identity(name="Carol"))
    # Alice and Bob both endorse Carol
    g.add_endorsement(Endorsement(endorser_id=alice.id, endorsee_id=carol.id))
    g.add_endorsement(Endorsement(endorser_id=bob.id, endorsee_id=carol.id))
    scores = compute_trust_scores(g)
    assert scores[carol.id] > scores[alice.id]
    assert scores[carol.id] > scores[bob.id]


def test_trust_scores_normalized():
    g = TrustGraph()
    alice = g.add_identity(Identity(name="Alice"))
    bob = g.add_identity(Identity(name="Bob"))
    g.add_endorsement(Endorsement(endorser_id=alice.id, endorsee_id=bob.id))
    scores = compute_trust_scores(g)
    assert max(scores.values()) == 1.0
    assert all(0.0 <= s <= 1.0 for s in scores.values())


# --- API tests ---

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_get_identity():
    r = client.post("/identities", json={"name": "Alice"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Alice"
    assert "id" in data

    r2 = client.get(f"/identities/{data['id']}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "Alice"


def test_get_identity_not_found():
    r = client.get("/identities/nonexistent")
    assert r.status_code == 404


def test_list_identities():
    client.post("/identities", json={"name": "Alice"})
    client.post("/identities", json={"name": "Bob"})
    r = client.get("/identities")
    assert len(r.json()) == 2


def test_delete_identity_removes_endorsements():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    bob = client.post("/identities", json={"name": "Bob"}).json()
    client.post("/endorsements", json={"endorser_id": alice["id"], "endorsee_id": bob["id"]})
    client.delete(f"/identities/{alice['id']}")
    assert len(graph.endorsements) == 0


def test_get_endorsers_and_endorsees():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    bob = client.post("/identities", json={"name": "Bob"}).json()
    client.post("/endorsements", json={"endorser_id": alice["id"], "endorsee_id": bob["id"]})

    r = client.get(f"/identities/{bob['id']}/endorsers")
    assert r.status_code == 200
    assert [e["endorser_id"] for e in r.json()] == [alice["id"]]

    r = client.get(f"/identities/{alice['id']}/endorsees")
    assert r.status_code == 200
    assert [e["endorsee_id"] for e in r.json()] == [bob["id"]]


def test_get_endorsers_not_found():
    r = client.get("/identities/nonexistent/endorsers")
    assert r.status_code == 404


def test_create_endorsement():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    bob = client.post("/identities", json={"name": "Bob"}).json()
    r = client.post("/endorsements", json={"endorser_id": alice["id"], "endorsee_id": bob["id"]})
    assert r.status_code == 201
    assert r.json()["endorser_id"] == alice["id"]


def test_delete_endorsement():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    bob = client.post("/identities", json={"name": "Bob"}).json()
    e = client.post("/endorsements", json={"endorser_id": alice["id"], "endorsee_id": bob["id"]}).json()
    r = client.delete(f"/endorsements/{e['id']}")
    assert r.status_code == 204
    assert len(graph.endorsements) == 0


def test_delete_endorsement_not_found():
    r = client.delete("/endorsements/nonexistent")
    assert r.status_code == 404


def test_create_endorsement_self():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    r = client.post("/endorsements", json={"endorser_id": alice["id"], "endorsee_id": alice["id"]})
    assert r.status_code == 400


def test_trust_scores_api():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    bob = client.post("/identities", json={"name": "Bob"}).json()
    client.post("/endorsements", json={"endorser_id": alice["id"], "endorsee_id": bob["id"]})
    r = client.get("/trust-scores")
    assert r.status_code == 200
    scores = r.json()
    assert alice["id"] in scores
    assert bob["id"] in scores


def test_trust_score_single_identity():
    alice = client.post("/identities", json={"name": "Alice"}).json()
    r = client.get(f"/trust-scores/{alice['id']}")
    assert r.status_code == 200
    assert r.json()["score"] == 1.0


def test_trust_score_not_found():
    r = client.get("/trust-scores/nonexistent")
    assert r.status_code == 404
