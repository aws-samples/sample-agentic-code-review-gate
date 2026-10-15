# Sample Agentic Code Review Gate

> **Non-production sample:** This is sample code for demonstration and educational purposes only. It is not intended for production use and should not be deployed without additional security review and testing.

This repository demonstrates how to implement an agentic code review gate.

> An AI code reviewer is a privileged principal that reads attacker-controlled
> input. Built naively it is a new attack surface. Built as a fail-closed
> security control it is a mitigation against AI-accelerated threats.

Two review lanes run on every pull request against the same small Python app,
using the same model and the same cloud credentials. Only the review *design*
differs.

## Design

Two independent model calls (discovery → falsification). Rules and prompts read from the **base** commit. Agent is code-only (`Read`,`Grep`,`Glob`) with a prefetched diff; it never sees the PR title, body, or comments. Credentials assumed last, checkout token not persisted, output redacted. Verdict parsed from SHA-scoped markers; every abnormal path fails closed. A CI step posts the comment.

The pattern is adapted from [KiroCrew](https://github.com/kirodotdev/KiroCrew)
(Apache-2.0), whose `.github/workflows/claude-review.yml` and
`.github/review-prompts/` run this design in production on a 7,000-commit
open-source repository. See its
[`docs/ci/ci-and-reviews.md`](https://github.com/kirodotdev/KiroCrew/blob/main/docs/ci/ci-and-reviews.md)
for the maintainers' rationale.

## The target

`app/files.py` serves assets under a root directory and refuses paths that
resolve outside it. `app/tokens.py` compares API tokens in constant time and
logs only a redacted form. `RULES.yaml` encodes three blocking rules the
reviewer enforces: `no-guard-removal`, `no-secret-logging`,
`rules-may-only-tighten`.

## Setting it up on GitHub

1. Create an empty repository and push `main`.
2. Auth for the model calls:
   - **Amazon Bedrock:** create an IAM role trusted by GitHub's
     OIDC provider for this repository with `bedrock:InvokeModel*` on the
     inference profiles you use; store its ARN as secret `AWS_BEDROCK_ROLE_ARN`.
     Optional variable `AWS_REGION` (default `us-west-2`).

3. Repository variables (optional): `DISCOVERY_MODEL` (default
   `us.anthropic.claude-sonnet-4-6`), `VALIDATION_MODEL` (default
   `us.anthropic.claude-opus-4-8`). Cheaper/faster discovery, stronger validation.

## What this does not solve

- A same-repo PR can still edit `agentic-review.yml` itself. Protect
  `.github/**` with CODEOWNERS and required review; handle fork PRs with a
  default-branch `workflow_run` lane (see KiroCrew's `fork-*.yml`).
- Models are nondeterministic. Two passes and a fail-closed gate raise the bar;
  they are not a proof. Measure.
- Latency and cost: two model calls per PR.

## License

Apache-2.0. Review prompts adapted from
[KiroCrew](https://github.com/kirodotdev/KiroCrew) (Apache-2.0, Copyright
Amazon.com, Inc. or its affiliates). See
[THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES) for attribution and license details.
