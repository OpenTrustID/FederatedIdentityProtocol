# Contributing to OpenTrust ID

Thanks for considering a contribution. This project is small on purpose — please keep
changes focused and consistent with the existing style.

## Getting started

```bash
git clone https://github.com/OpenTrustID/FederatedIdentityProtocol
cd FederatedIdentityProtocol
pip install -e ".[dev]"
```

## Development workflow

1. Create a branch off `main`.
2. Make your change.
3. Run the test suite and linter:
   ```bash
   pytest tests/ -v
   ruff check .
   ```
4. Add or update tests for any behavior change. Bug fixes should include a regression test.
5. Open a pull request describing what changed and why.

## Reporting issues

Open a GitHub issue with:
- What you expected to happen.
- What actually happened.
- Steps to reproduce (a `curl` sequence against the API is ideal).

## Design principles

- **The trust graph is the source of truth.** Trust scores are always derived, never stored.
- **No centralized identity verification.** Endorsements are the only signal — avoid adding
  features that reintroduce a centralized authority.
- **Keep the API surface small and predictable.** Prefer extending existing resources over
  adding new ones.
