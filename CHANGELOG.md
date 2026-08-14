# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `DELETE /endorsements/{id}` to revoke an endorsement.
- `GET /identities/{id}/endorsers` and `GET /identities/{id}/endorsees` to inspect an
  identity's incoming and outgoing endorsements directly.
- `GET /health` liveness endpoint reporting graph size.
- CORS middleware, configurable via `OPENTRUST_CORS_ORIGINS`.
- Environment-based configuration for host, port, log level, and CORS origins.
- Structured logging for identity and endorsement mutations.
- `Dockerfile` and `.dockerignore` for containerized deployment.
- GitHub Actions CI running the test suite and `ruff` lint on every push and PR.
- MIT `LICENSE`, `CONTRIBUTING.md`.

### Changed
- Re-endorsing the same endorser/endorsee pair now updates the existing endorsement's
  weight and note in place instead of appending a duplicate edge, preventing a single
  relationship from inflating a trust score through repeated endorsement.

## [0.1.0] - Initial release

- Core trust graph model: `Identity`, `Endorsement`, `TrustGraph`.
- PageRank-style trust score propagation (`compute_trust_scores`).
- FastAPI REST API for identities, endorsements, and trust scores.
