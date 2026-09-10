# Contributing

Contributions that make the operator safer, clearer, more portable, or more
evidence-led are welcome.

## Before you start

- Open an issue for a substantial workflow or policy change.
- Keep provider behavior grounded in current official documentation.
- Preserve review-first external mutations and dry-run defaults.
- Do not add ranking guarantees, forced-indexing claims, content quotas, link
  schemes, fabricated experience, or detector-evasion features.
- Do not commit credentials, account data, live project state, raw social
  research, or private paths.

## Development setup

The helper scripts require Python 3.10 or newer and have no runtime package
dependencies.

```bash
python3 scripts/test_operator.py
python3 -m py_compile scripts/*.py
```

The repository validator uses PyYAML:

```bash
python3 -m pip install PyYAML==6.0.2
python3 scripts/validate_skill.py .
```

## Pull requests

Keep changes focused. Explain the user problem, decision rule, risks, evidence,
and tests. Update the README and changelog when commands or public behavior
change. Add a concise ADR only for a durable, surprising trade-off that would be
costly to reverse.

By contributing, you agree that your contribution is licensed under this
repository's MIT License.
