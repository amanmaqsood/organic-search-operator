# Generate all three discovery files on the first automation run

Every project creates `llms.txt`, `llms-full.txt`, and experimental `ai.txt`
from a reviewed public canonical-content manifest on its first automation run,
then updates generator-owned files only when that source changes. This accepts
the maintenance cost of three public files to provide one predictable
machine-readable layer across projects, while explicitly rejecting any ranking
promise: Google says it ignores these files, `ai.txt` has no universal platform
standard, canonical HTML remains authoritative, and ownership hashes prevent
the automation from overwriting unmanaged or manually changed content.
