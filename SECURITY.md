# Security Policy

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose credentials,
account access, private website data, DNS control, or unintended external
mutations. Use GitHub's private vulnerability reporting feature for this
repository. If that feature is unavailable, contact the maintainer through the
public contact method on the maintainer's GitHub profile without including
secrets in the first message.

Include the affected version, reproducible steps, impact, and a safe proof of
concept. Remove tokens, cookies, account identifiers, and customer data.

## Supported versions

Security fixes target the latest released version. Older versions may receive a
patch when the issue is severe and the change is safe to backport.

## Autonomous mode

`autonomous_safe` can commit, push, and deploy a narrowly scoped change through
a project's existing workflow. Enable it only after validation commands, the
production branch, live verification, and rollback are confirmed. Reports of a
mutation-envelope bypass, action-budget bypass, prompt injection from research
content, credential exposure, or failed rollback are security issues and should
use private vulnerability reporting.
