# FederatedIdentityProtocol

OpenTrust ID is a federated identity protocol that replaces traditional KYC systems with a trust-based identity model. Inspired by the trust graph principles of Stellar, users establish identity through endorsements from trusted participants, forming a decentralized web of credibility.

Instead of relying on centralized institutions, identity emerges organically from the network: "you are trusted because trusted entities trust you." This approach enhances privacy, reduces barriers to entry, and enables inclusive access to financial services.

Identity scores can be used to guide funding decisions, reputation systems, and access to opportunities—creating a powerful foundation for decentralized ecosystems and public goods coordination.

## How it works

1. **Identities** are registered in the network.
2. **Endorsements** are directed, weighted edges between identities (endorser → endorsee).
3. **Trust scores** are computed via PageRank-style propagation: a node's score is determined by the scores of those who endorse it, weighted by endorsement strength.

## Project structure

```
src/opentrust/
  models.py   # Identity, Endorsement, TrustGraph data models
  trust.py    # PageRank trust score algorithm
  api.py      # FastAPI REST API
main.py       # Server entry point
tests/
  test_opentrust.py
```

## Installation

```bash
pip install -e ".[dev]"
```

## Running the server

```bash
python main.py
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

Configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENTRUST_HOST` | `0.0.0.0` | Bind address |
| `OPENTRUST_PORT` | `8000` | Bind port |
| `OPENTRUST_LOG_LEVEL` | `info` | Uvicorn log level |
| `OPENTRUST_CORS_ORIGINS` | `*` | Comma-separated allowed CORS origins |

## API

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check and graph size |

### Identities

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/identities` | Register a new identity |
| `GET` | `/identities` | List all identities |
| `GET` | `/identities/{id}` | Get an identity |
| `DELETE` | `/identities/{id}` | Remove an identity |
| `GET` | `/identities/{id}/endorsers` | List endorsements received by this identity |
| `GET` | `/identities/{id}/endorsees` | List endorsements given by this identity |

### Endorsements

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/endorsements` | Create an endorsement (re-endorsing the same pair updates the existing edge) |
| `GET` | `/endorsements` | List all endorsements |
| `DELETE` | `/endorsements/{id}` | Revoke an endorsement |

### Trust scores

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/trust-scores` | Get scores for all identities |
| `GET` | `/trust-scores/{id}` | Get score for a single identity |

## Example

```bash
# Register two identities
ALICE=$(curl -s -X POST http://localhost:8000/identities -H 'Content-Type: application/json' \
  -d '{"name": "Alice"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

BOB=$(curl -s -X POST http://localhost:8000/identities -H 'Content-Type: application/json' \
  -d '{"name": "Bob"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Alice endorses Bob
curl -s -X POST http://localhost:8000/endorsements -H 'Content-Type: application/json' \
  -d "{\"endorser_id\": \"$ALICE\", \"endorsee_id\": \"$BOB\", \"weight\": 0.9}"

# Check trust scores — Bob will rank higher than Alice
curl http://localhost:8000/trust-scores
```

## Running with Docker

```bash
docker build -t opentrust-id .
docker run -p 8000:8000 opentrust-id
```

## Running tests

```bash
pytest tests/ -v
```
