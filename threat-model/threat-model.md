# Comprehensive Threat Model Report

**Generated**: 2026-09-25 21:22:38
**Current Phase**: 1 - Business Context Analysis
**Overall Completion**: 100.0%

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Context](#business-context)
3. [Classification Profiles](#classification-profiles)
4. [System Architecture](#system-architecture)
5. [Threat Actors](#threat-actors)
6. [Trust Boundaries](#trust-boundaries)
7. [Assets and Flows](#assets-and-flows)
8. [Threats](#threats)
9. [Mitigations](#mitigations)
10. [Assumptions](#assumptions)
11. [Phase Progress](#phase-progress)

## Executive Summary

Public, Apache-2.0 sample repository (sample-agentic-code-review-gate) built for a security-conference demo. It shows an AI code reviewer designed as a fail-closed security control: a GitHub Actions workflow (.github/workflows/agentic-review.yml) runs two independent Claude model calls (discovery, then falsification/validation) against every same-repo pull request, using Amazon Bedrock via GitHub OIDC (secret AWS_BEDROCK_ROLE_ARN) or the Anthropic API (secret ANTHROPIC_API_KEY). Rules (RULES.yaml) and prompts (.github/review-prompts/*.md) are read from the PR BASE commit; the agent is code-only (Read/Grep/Glob) with a prefetched diff; a CI step parses SHA-scoped markers ([REVIEWED]/[BLOCK-MERGE]) and posts one PR comment; every abnormal path fails closed. The review target is a tiny Python asset service (app/files.py path containment, app/tokens.py constant-time token check with redacted logging) that is deliberately attacked by four demo PRs (guard removal, prompt injection, rules disarming, CI credential exfiltration). The README also describes a deliberately insecure naive lane and demo tooling that are not present in this checkout. Business value: reputational (a security sample must not itself be exploitable) and educational; the assets that matter are the integrity of the merge gate, the cloud/API credentials the workflow holds, and the cost of model invocations.

### Key Statistics

- **Total Threats**: 24
- **Total Mitigations**: 30
- **Total Assumptions**: 21
- **System Components**: 15
- **Assets**: 12
- **Threat Actors**: 15

## Business Context

**Description**: Public, Apache-2.0 sample repository (sample-agentic-code-review-gate) built for a security-conference demo. It shows an AI code reviewer designed as a fail-closed security control: a GitHub Actions workflow (.github/workflows/agentic-review.yml) runs two independent Claude model calls (discovery, then falsification/validation) against every same-repo pull request, using Amazon Bedrock via GitHub OIDC (secret AWS_BEDROCK_ROLE_ARN) or the Anthropic API (secret ANTHROPIC_API_KEY). Rules (RULES.yaml) and prompts (.github/review-prompts/*.md) are read from the PR BASE commit; the agent is code-only (Read/Grep/Glob) with a prefetched diff; a CI step parses SHA-scoped markers ([REVIEWED]/[BLOCK-MERGE]) and posts one PR comment; every abnormal path fails closed. The review target is a tiny Python asset service (app/files.py path containment, app/tokens.py constant-time token check with redacted logging) that is deliberately attacked by four demo PRs (guard removal, prompt injection, rules disarming, CI credential exfiltration). The README also describes a deliberately insecure naive lane and demo tooling that are not present in this checkout. Business value: reputational (a security sample must not itself be exploitable) and educational; the assets that matter are the integrity of the merge gate, the cloud/API credentials the workflow holds, and the cost of model invocations.

### Business Features

- **Industry Sector**: Technology
- **Data Sensitivity**: Confidential
- **User Base Size**: Nano
- **Geographic Scope**: Global / Transboundary
- **Regulatory Requirements**: None
- **System Criticality**: Low
- **Financial Impact**: Low
- **Authentication Requirement**: Federated
- **Deployment Model**: SaaS
- **User Base Metric**: Registered users
- **Revenue Band**: Enterprise
- **Data Residency**: National / Single-Country
- **Compute Location**: National / Single-Country
- **User Base Location**: Global / Transboundary
- **Organizational HQ**: National / Single-Country

## Classification Profiles

### Software Profile

- **Software Type**: Developer Tooling / CI-CD System
- **Deployment Model**: SaaS
- **Architecture Style**: Event-driven
- **Platform / Runtime**: Cloud runtime
- **User Domain**: Security
- **Licensing / Ownership**: Open source
- **Modern Paradigms**: Agentic AI, AI/ML, Cloud-native, Event-driven architecture
- **Description**: GitHub Actions workflow triggered by pull_request events (opened/synchronize/reopened). Job steps: checkout (persist-credentials=false, fetch-depth 0) -> extract RULES.yaml and prompts from BASE sha into .review-base/.review-prompts (fail if missing) -> prefetch diff base...head into $RUNNER_TEMP/pr.diff (fail if empty) -> assume AWS role via OIDC (aws-actions/configure-aws-credentials, only if AWS_BEDROCK_ROLE_ARN set) -> Discovery pass (anthropics/claude-code-action, model DISCOVERY_MODEL default us.anthropic.claude-sonnet-4-6, --allowedTools Read,Grep,Glob, --max-turns 40) -> capture candidates from execution_file, redact, fail closed on missing [DISCOVERY] marker or >120000 bytes -> Validation pass (same action, model VALIDATION_MODEL default us.anthropic.claude-opus-4-8) -> capture+redact review-output.md -> CI step posts/updates ONE PR comment keyed by hidden marker via gh api (GITHUB_TOKEN) -> gate step exits 1 unless [REVIEWED] <head sha> present and [BLOCK-MERGE] <head sha> absent. Every step is guarded by head.repo.full_name == github.repository (fork guard). Third-party actions are pinned by commit SHA. Permissions: contents read, pull-requests write, id-token write. Concurrency group per PR with cancel-in-progress. A separate ci.yml runs pytest. The demo app is a pure-Python library (no HTTP layer in this checkout).

### Data Asset Profiles

| ID | Name | Asset | Category | Content Types | Sensitivity | Compliance | States | Volume | Lifecycle | Business Domain | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DP001 | Pull request diff and repository source code | DA-PR-CODE | Unstructured Data | Non-sensitive / other | Public | None | At rest, In transit, In use | Small | Active | Engineering | Attacker-controllable input: the base...head diff prefetched to $RUNNER_TEMP/pr.diff plus the full checkout the agent may Read/Grep/Glob. Public Apache-2.0 code, so confidentiality is low; integrity of what the reviewer judges is what matters. |
| DP002 | Review contract: RULES.yaml, review prompts, agentic-review.yml | DA-CONTRACT | Configuration Data | System metadata | Internal | None | At rest, In use | Small | Active | Engineering | Defines what the reviewer enforces and how the gate decides. Read from the BASE commit at runtime. Integrity-critical: weakening it is itself a blocking violation (rules-may-only-tighten). The workflow file itself is only protected by repository branch protection/CODEOWNERS, which this repo does not ship. |
| DP003 | Workflow credentials: GITHUB_TOKEN, AWS OIDC role ARN and STS session credentials, ANTHROPIC_API_KEY | DA-CREDS | Secrets and Credentials | Authentication credentials | Restricted | None | In transit, In use | Small | Active | Engineering | GITHUB_TOKEN (contents:read, pull-requests:write, id-token:write) is handed to claude-code-action and the comment step; short-lived AWS credentials from aws-actions/configure-aws-credentials live in the job environment for the model-call steps; ANTHROPIC_API_KEY is an optional fallback. Exposure enables PR-comment spoofing, model-invocation cost abuse, or Bedrock access within the role's policy. |
| DP004 | Model outputs: discovery candidates, validation verdict, posted PR comment | DA-VERDICT | Unstructured Data | Operational / telemetry data | Internal | None | At rest, In transit, In use | Small | Active | Engineering | .review-candidates.md (never posted), review-output.md (posted after regex redaction), and the SHA-scoped markers the gate parses. Integrity of the verdict is the whole point of the system; the comment is public on a public repo. |
| DP005 | Workflow run logs and Claude execution transcripts | DA-LOGS | Semi-Structured Data | Operational / telemetry data | Internal | None | At rest | Small | Active | Engineering | GitHub Actions logs (the workflow cats redacted candidates and review output) and the claude-code-action execution_file. Readable by anyone with read access to the repository; on a public repository that is everyone. |
| DP006 | Demo asset service data: API token and files under the asset root | DA-APP | Secrets and Credentials | Authentication credentials, Non-sensitive / other | Confidential | None | At rest, In use | Small | Active | Engineering | The review target's own data: the expected API token compared in app/tokens.py and the files served from asset_root in app/files.py. Not deployed anywhere in this sample; modelled because the attack PRs target these controls and the reviewer must catch their weakening. |

### User Personas

| ID | Persona | Name | Privilege | Affiliation | Roles | Intent | Entity Type | Authentication | Threat Actor Overlay | In Scope | Description |
|---|---|---|---|---|---|---|---|---|---|---|---|
| UP001 | Developer / DevOps User | Repository maintainer / demo presenter | Administrative | Employee | Administrator, Approver, Developer, Data Owner | Legitimate | Human | Multi-factor | Mistaken configuration (branch protection, OIDC trust policy, secrets) | Yes | Owns the GitHub repository, configures secrets (AWS_BEDROCK_ROLE_ARN, ANTHROPIC_API_KEY, DEMO_FAKE_SECRET), variables, branch protection and the IAM role trust policy. Can bypass the gate by design of GitHub if admin bypass is left enabled. |
| UP002 | Developer / DevOps User | Same-repository contributor (write access) | Elevated | Employee | Developer | Malicious | Human | Multi-factor | Malicious insider, Compromised developer account | Yes | Can push branches and open PRs that run agentic-review.yml WITH repository secrets. This is the adversary the four demo attack PRs model: smuggles guard removal, plants prompt injection in code comments and PR body, disarms RULES.yaml/prompts, adds conftest.py that exfiltrates CI secrets. |
| UP003 | Authenticated Standard User | Fork contributor (external GitHub user) | Low | Public / Unknown | Developer | Malicious | Human | Password | Opportunistic attacker, Script kiddie | Yes | Any GitHub account can open a fork PR against a public repository. The workflow renders the check name but every step is skipped for fork PRs; secrets are not passed to fork-triggered pull_request runs. A fork PR still exercises ci.yml (pytest) without secrets. |
| UP004 | Non-Human Identity / Service Account | GitHub Actions workflow identity (GITHUB_TOKEN) | Elevated | Employee | Service Account, Operator | Legitimate | Non-Human | Token | Abused via workflow-file edits | Yes | Job-scoped token with contents:read, pull-requests:write, id-token:write. Posts/updates the review comment, requests the OIDC token used to assume the Bedrock role, and is passed to anthropics/claude-code-action as github_token. |
| UP005 | Non-Human Identity / Service Account | AI reviewer agent (Claude Code via claude-code-action) | Medium | Vendor | Service Account, Auditor | Compromised | Non-Human | IAM Role | Prompt-injected agent, Confused deputy | Yes | Two invocations (discovery, validation) with --allowedTools Read,Grep,Glob and --max-turns 40, running on the runner with the AWS session credentials in its process environment and the prefetched diff plus full checkout on disk. Reads attacker-controlled text; modelled as potentially compromised (prompt injection) so its only output channel, the final message, is treated as untrusted by CI. |
| UP006 | External Service / Third-Party Integration | Model provider: Amazon Bedrock or Anthropic API | Low | Vendor | Integration Endpoint | Legitimate | External System | IAM Role | N/A | Yes | Receives the diff, any files the agent reads, and the prompts; returns the model output. Bedrock in vars.AWS_REGION (default us-west-2) via the OIDC-assumed role, or api.anthropic.com with ANTHROPIC_API_KEY. |
| UP007 | External Service / Third-Party Integration | Third-party GitHub Actions (checkout, setup-python, configure-aws-credentials, claude-code-action) | Elevated | Vendor | Integration Endpoint | Legitimate | External System | None | Supply-chain compromise | Yes | Code executed inside the job with access to GITHUB_TOKEN and, for claude-code-action, the AWS session credentials. All four are pinned to full commit SHAs with version comments. claude-code-action installs the Claude Code CLI at run time. |
| UP008 | Anonymous / Unauthenticated User | Public reader / demo audience | None | Public / Unknown | End User | Legitimate | Human | None | Passive observer of leaked data in logs/comments | Yes | Anyone can read the public repository, PR comments (including the posted review), and Actions logs (which contain the redacted candidate list and review output). |
| UP009 | Authenticated Standard User | Asset service client (demo app) | Low | Customer | End User | Malicious | Human | Token | Path traversal attacker, Token brute-force | Yes | Hypothetical caller of app.files.read_asset(asset_root, requested) and app.tokens.verify_token(presented, expected). Supplies the requested path and the presented token; modelled malicious because the demo PRs try to weaken exactly these two controls. |

### Non-Functional Requirements

- **Fail-Safe Behaviour**: Revert to safe state — Core design property: missing prompt, empty diff, missing [DISCOVERY]/[REVIEWED] marker, oversized candidates, errored step, or [BLOCK-MERGE] all exit 1 and block the merge.
- **Faultlessness**: Medium — LLM verdicts are nondeterministic; two passes plus a closed blocking list raise the bar but the README asks for empirical measurement (10 runs per attack) rather than assuming correctness.
- **Availability**: 99% — Depends on GitHub Actions, GitHub-hosted runners and Bedrock/Anthropic availability. Outages block merges (fail closed) rather than allowing them; acceptable for a demo repository.
- **Recoverability**: Hours — Recovery is a workflow re-run; no persistent state beyond PR comments.
- **Time Behaviour**: Standard — Two sequential model calls per PR, job timeout 30 minutes, --max-turns 40 per pass.
- **Resource Utilization**: Moderate — Model invocation cost per PR is the main resource; concurrency group cancels superseded runs per PR.
- **Capacity**: Small — Nano user base; a handful of PRs per demo.
- **Scalability**: Elastic — GitHub-hosted runners and Bedrock scale on demand; cost scales with them.
- **Analysability**: High — Deterministic gate on SHA-scoped markers, transcripts and redacted outputs in logs, execution_file from the action.
- **Testability**: High — README describes tests/test_workflow_invariants.py and tests/test_gate.py pinning the security properties (not present in this checkout).
- **User Error Protection**: Strong — Operator mistakes (missing prompt on base, unset secrets) fail the job instead of silently passing.
- **Fault Tolerance**: Partial — No retries; a transient model or runner failure fails the check and requires a manual re-run.
- **Adaptability**: Multiple environments — Bedrock via OIDC or direct Anthropic API, selected at run time by secret presence; model ids via repository variables.
- **Interoperability**: Standards-based — GitHub OIDC to AWS STS, GitHub Checks/branch protection, REST API via gh.
- **Co-existence**: Shared environment — Runs alongside ci.yml and (per README) a naive review lane against the same PRs.
- **Operability**: Standard — Configured through repository secrets/variables and branch protection; one PR comment updated in place.
- **Installability**: Scripted — Copy workflow, prompts and RULES.yaml; demo/reset.sh (not in checkout) recreates demo PRs.
- **Modularity**: Medium — Prompts, rules and workflow are separate files; gate logic is inline shell in the workflow.
- **Replaceability**: Partially substitutable — Model provider is swappable; GitHub Actions and claude-code-action specifics are not.
- **Safety Criticality**: Non-safety-related — Software supply-chain control; no physical safety impact.
- **Accessibility / Inclusivity**: None specified — Developer tooling surfaced through GitHub's UI.

## System Architecture

### Components

| ID | Name | Type | Service Provider | Description |
|---|---|---|---|---|
| C001 | Pull request author client (git / GitHub web) | Other | Other | Entry point for all attacker-controlled input: branch pushes, PR open/synchronize/reopen events, PR title and body, and file content (code, comments, filenames, symlinks, conftest.py). Same-repo authors have write access; fork authors do not. |
| C002 | GitHub repository and pull request platform | Other | Other | Hosts main and PR branches, the review contract on main, PR conversations where the verdict comment is posted, check runs, and the branch protection rules that make the check a merge gate (README setup step 4). |
| C003 | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) | Security | Other | Dispatches pull_request events to agentic-review.yml and ci.yml, injects repository secrets/variables and the job-scoped GITHUB_TOKEN, mints the OIDC ID token (id-token: write), records the check conclusion from the job exit code, and applies the concurrency group agentic-review-<pr>. |
| C004 | GitHub-hosted runner (ubuntu-latest) executing job agentic-review | Compute | Other | Ephemeral VM that runs every step of the review job. Holds GITHUB_TOKEN, and after the credentials step the AWS session credentials, in process environment. All steps carry the fork guard head.repo.full_name == github.repository. |
| C005 | Contract and diff preparation steps (actions/checkout, extract base-ref rules and prompts, prefetch diff) | Compute | Other | CONTROL 1 and CONTROL 2 part 1: checkout with persist-credentials=false and fetch-depth 0; rm -rf then recreate .review-base/.review-prompts; git show $BASE_SHA:RULES.yaml and both prompts (exit 1 if missing/empty); git diff base...head into $RUNNER_TEMP/pr.diff (exit 1 if empty). |
| C006 | aws-actions/configure-aws-credentials (OIDC to STS) | Security | AWS | CONTROL 3: runs only when USE_BEDROCK == 'true'; exchanges the GitHub OIDC token for short-lived STS credentials for secrets.AWS_BEDROCK_ROLE_ARN in vars.AWS_REGION (default us-west-2) and exports them into the job environment for the remaining steps. |
| C007 | Discovery agent (anthropics/claude-code-action pass 1) | Compute | Other | CONTROL 2 part 2 / CONTROL 4 stage 1: reads .review-prompts/discovery.md, the prefetched diff and any repository file via Read/Grep/Glob, and emits a candidate list ending in [DISCOVERY] <head sha>. Receives github_token and anthropic_api_key inputs and inherits AWS session credentials from the environment. Installs the Claude Code CLI at run time. |
| C008 | Validation agent (anthropics/claude-code-action pass 2) | Compute | Other | CONTROL 4 stage 2: independent invocation that reads .review-prompts/validate.md, the diff, the repository and .review-candidates.md (treated as untrusted evidence), falsifies candidates, classifies survivors against the closed BLOCKING list, and emits [REVIEWED] <sha> plus optionally [BLOCK-MERGE] <sha>. Only this pass's output reaches the PR. |
| C009 | Capture, redact, comment and gate steps (CI shell) | Security | Other | CONTROL 5: extracts the last result from each pass's execution_file with jq; perl-redacts AKIA/ASIA key ids, arn:aws*, 12-digit account ids and labelled secret values; fails closed if [DISCOVERY] marker is missing or candidates exceed 120000 bytes; posts or updates ONE PR comment keyed by <!-- agentic-ai-review --> (filtered to github-actions[bot] author) using GITHUB_TOKEN; final gate exits 1 unless validate.outcome == success, review-output.md non-empty, [REVIEWED] <sha> present and [BLOCK-MERGE] <sha> absent. |
| C010 | AWS IAM role for Bedrock (AWS_BEDROCK_ROLE_ARN) and AWS STS | Security | AWS | IAM role trusted by GitHub's OIDC provider (token.actions.githubusercontent.com) for this repository; policy should grant only bedrock:InvokeModel* on the inference profiles used (README setup step 2). Configuration lives outside the repository. |
| C011 | Amazon Bedrock (Anthropic Claude inference profiles) | Analytics | AWS | Model provider on the recommended path. Receives prompts, the diff and any file content the agent reads; returns model output. Cross-region inference profile ids us.anthropic.claude-sonnet-4-6 and us.anthropic.claude-opus-4-8 by default. |
| C012 | Anthropic API (fallback model provider) | Other | Other | Used when AWS_BEDROCK_ROLE_ARN is not set and ANTHROPIC_API_KEY is. Long-lived API key passed as an action input to both agent steps; model ids must be overridden via repository variables. |
| C013 | Public package registries and release endpoints (PyPI, npm/Bun, GitHub Releases) | Other | Other | Run-time downloads: ci.yml installs pytest==8.4.1 and PyYAML==6.0.2 from PyPI; claude-code-action installs the Claude Code CLI; setup-python fetches interpreters. Third-party actions themselves are fetched from GitHub by pinned commit SHA. |
| C014 | CI unit test job (ci.yml, pytest on ubuntu-latest) | Compute | Other | Separate workflow on pull_request and push to main: checkout (persist-credentials=false), setup-python 3.12, pip install pytest/PyYAML, python -m pytest -q. Executes PR-controlled code (tests, conftest.py) with contents:read only and no repository secrets; runs for fork PRs too. Attack 4 in the README targets this job. |
| C015 | Demo asset service library (app/files.py, app/tokens.py) | Compute | Other | The review target. resolve_asset() rejects empty/padded/absolute paths and any path whose resolve() (symlinks followed) is not under the resolved asset root, then read_asset() returns bytes. verify_token() compares with hmac.compare_digest and logs only describe_token() (4-char prefix + length) on failure. These are the guards RULES.yaml no-guard-removal and no-secret-logging protect. |

### Connections

| ID | Source | Destination | Protocol | Port | Encrypted | Description |
|---|---|---|---|---|---|---|
| CN001 | Pull request author client (git / GitHub web) (C001) | Git repository content (main and PR branches) (D001) | HTTPS | 443 | Yes | git push of PR branch; PR open/synchronize/reopen; PR title/body edits. Authenticated GitHub identity, attacker-controlled content. |
| CN002 | GitHub repository and pull request platform (C002) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | HTTPS | 443 | Yes | pull_request event (opened/synchronize/reopened) dispatched to agentic-review.yml and ci.yml; event payload includes head/base SHAs, head.repo.full_name, PR number. |
| CN003 | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | HTTPS | 443 | Yes | Job assignment to a fresh runner: workflow definition from the PR merge/head ref, GITHUB_TOKEN with declared permissions, repository secrets and variables (same-repo PRs only). |
| CN004 | GitHub Actions secrets and variables store (D002) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | Other | N/A | Yes | Secrets/variables injected into the job: AWS_BEDROCK_ROLE_ARN (used in env presence test and role-to-assume), ANTHROPIC_API_KEY, DISCOVERY_MODEL, VALIDATION_MODEL, AWS_REGION. |
| CN005 | Contract and diff preparation steps (actions/checkout, extract base-ref rules and prompts, prefetch diff) (C005) | Git repository content (main and PR branches) (D001) | HTTPS | 443 | Yes | actions/checkout clones the PR head with fetch-depth 0 using GITHUB_TOKEN; persist-credentials=false so the token is not written to .git/config. |
| CN006 | Contract and diff preparation steps (actions/checkout, extract base-ref rules and prompts, prefetch diff) (C005) | Runner ephemeral workspace and process environment (D003) | Other | N/A | No | Writes .review-base/RULES.yaml and .review-prompts/{discovery,validate}.md from git show $BASE_SHA:..., and $RUNNER_TEMP/pr.diff from git diff base...head. Scratch dirs are rm -rf'ed first so PR-committed files/symlinks at those paths cannot redirect writes. |
| CN007 | aws-actions/configure-aws-credentials (OIDC to STS) (C006) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | HTTPS | 443 | Yes | Requests the GitHub OIDC ID token (ACTIONS_ID_TOKEN_REQUEST_URL/TOKEN) for audience sts.amazonaws.com. |
| CN008 | aws-actions/configure-aws-credentials (OIDC to STS) (C006) | AWS IAM role for Bedrock (AWS_BEDROCK_ROLE_ARN) and AWS STS (C010) | HTTPS | 443 | Yes | sts:AssumeRoleWithWebIdentity with the OIDC token for secrets.AWS_BEDROCK_ROLE_ARN; returns short-lived credentials exported to the job environment. |
| CN009 | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Runner ephemeral workspace and process environment (D003) | Other | N/A | No | Read/Grep/Glob over the checkout, .review-prompts/discovery.md, .review-base/RULES.yaml and $RUNNER_TEMP/pr.diff. Tool access is to the whole runner filesystem, not just the repo. Execution transcript written to execution_file. |
| CN010 | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Amazon Bedrock (Anthropic Claude inference profiles) (C011) | HTTPS | 443 | Yes | Bedrock Runtime InvokeModel/Converse (SigV4 with STS session credentials) carrying prompts, diff and read file content; returns discovery candidates. |
| CN011 | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Anthropic API (fallback model provider) (C012) | HTTPS | 443 | Yes | Fallback: Anthropic Messages API with ANTHROPIC_API_KEY when Bedrock is not configured. |
| CN012 | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Public package registries and release endpoints (PyPI, npm/Bun, GitHub Releases) (C013) | HTTPS | 443 | Yes | claude-code-action installs the Claude Code CLI at run time (version chosen by the action) while AWS session credentials are already present in the environment. |
| CN013 | Capture, redact, comment and gate steps (CI shell) (C009) | Runner ephemeral workspace and process environment (D003) | Other | N/A | No | Reads discovery execution_file with jq, writes and perl-redacts .review-candidates.md; reads validation execution_file, writes and redacts review-output.md; writes /tmp/review-comment.md. |
| CN014 | Validation agent (anthropics/claude-code-action pass 2) (C008) | Runner ephemeral workspace and process environment (D003) | Other | N/A | No | Read/Grep/Glob over the checkout, .review-prompts/validate.md, .review-base/RULES.yaml, $RUNNER_TEMP/pr.diff and .review-candidates.md (untrusted evidence). |
| CN015 | Validation agent (anthropics/claude-code-action pass 2) (C008) | Amazon Bedrock (Anthropic Claude inference profiles) (C011) | HTTPS | 443 | Yes | Bedrock Runtime InvokeModel/Converse for the validation model; returns the review with [REVIEWED]/[BLOCK-MERGE] markers. |
| CN016 | Validation agent (anthropics/claude-code-action pass 2) (C008) | Anthropic API (fallback model provider) (C012) | HTTPS | 443 | Yes | Fallback: Anthropic Messages API for the validation pass. |
| CN017 | Validation agent (anthropics/claude-code-action pass 2) (C008) | Public package registries and release endpoints (PyPI, npm/Bun, GitHub Releases) (C013) | HTTPS | 443 | Yes | Second run-time install of the Claude Code CLI by the action (or cached from pass 1). |
| CN018 | Capture, redact, comment and gate steps (CI shell) (C009) | Pull request conversation and check runs (D004) | HTTPS | 443 | Yes | gh api repos/$REPO/issues/$PR/comments --paginate (find existing bot comment starting with marker), gh api PATCH issues/comments/<id>, or gh pr comment --body-file; authenticated with GITHUB_TOKEN (pull-requests: write). |
| CN019 | Capture, redact, comment and gate steps (CI shell) (C009) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | Other | N/A | Yes | Gate step exit code (0 pass / 1 fail) becomes the job conclusion; ::error:: annotations; step logs streamed to the run log. |
| CN020 | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | Pull request conversation and check runs (D004) | Other | N/A | Yes | Check run 'Agentic AI Review' conclusion recorded on the PR head SHA; branch protection reads it to allow or block merge. |
| CN021 | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub Actions run logs and execution transcripts (D005) | Other | N/A | Yes | Run logs (including cat of redacted candidates and review output) and transcript output persisted for the repository's log retention period. |
| CN022 | CI unit test job (ci.yml, pytest on ubuntu-latest) (C014) | Git repository content (main and PR branches) (D001) | HTTPS | 443 | Yes | ci.yml checkout of the PR head (persist-credentials=false) for both same-repo and fork PRs. |
| CN023 | CI unit test job (ci.yml, pytest on ubuntu-latest) (C014) | Public package registries and release endpoints (PyPI, npm/Bun, GitHub Releases) (C013) | HTTPS | 443 | Yes | setup-python interpreter download and pip install pytest==8.4.1 PyYAML==6.0.2 from PyPI. |
| CN024 | CI unit test job (ci.yml, pytest on ubuntu-latest) (C014) | Demo asset service library (app/files.py, app/tokens.py) (C015) | Other | N/A | No | python -m pytest -q imports and executes PR-controlled test code (including any conftest.py) against app/; runs with contents:read GITHUB_TOKEN and no repository secrets. |
| CN025 | Demo asset service library (app/files.py, app/tokens.py) (C015) | Demo asset root directory (files served by app/files.py) (D006) | Other | N/A | No | resolve_asset()/read_asset() open files under asset_root after the resolved-path containment check; the demo bypass target is a file outside the root. |
| CN026 | Discovery agent (anthropics/claude-code-action pass 1) (C007) | GitHub repository and pull request platform (C002) | HTTPS | 443 | Yes | claude-code-action receives github_token as an input; whether it calls the GitHub API in this prompt-driven mode (e.g., to fetch PR context) is not verifiable from this repository and is treated as a possible channel for PR title/body to reach the agent. |

### Data Stores

| ID | Name | Type | Classification | Encrypted at Rest | Description |
|---|---|---|---|---|---|
| D001 | Git repository content (main and PR branches) | Other | Public | Yes | Source of both the trusted review contract (RULES.yaml, .github/review-prompts/*.md, .github/workflows/*.yml on the BASE commit) and the untrusted PR head content. Public repository. Protected only by branch protection on main; no CODEOWNERS shipped. |
| D002 | GitHub Actions secrets and variables store | Other | Restricted | Yes | Secrets AWS_BEDROCK_ROLE_ARN, ANTHROPIC_API_KEY (optional), DEMO_FAKE_SECRET (attack 4 demo); variables DISCOVERY_MODEL, VALIDATION_MODEL, AWS_REGION. Injected into same-repo pull_request runs only. |
| D003 | Runner ephemeral workspace and process environment | File System | Confidential | No | Checkout of the PR head, .review-base/RULES.yaml, .review-prompts/*.md, $RUNNER_TEMP/pr.diff, .review-candidates.md, review-output.md, /tmp/review-comment.md, claude-code-action execution_file; process environment holds GITHUB_TOKEN inputs and AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_SESSION_TOKEN after the credentials step. Destroyed with the VM. |
| D004 | Pull request conversation and check runs | Other | Public | Yes | Where the single review comment (marker <!-- agentic-ai-review -->) is posted/updated and where the 'Agentic AI Review' check conclusion is recorded for branch protection. Public on a public repository. |
| D005 | GitHub Actions run logs and execution transcripts | Other | Public | Yes | Step logs including 'cat' of the redacted candidate list and review output, claude-code-action transcript output, and gh/jq errors. Readable by anyone who can read the repository; retained per GitHub default (90 days). |
| D006 | Demo asset root directory (files served by app/files.py) | File System | Confidential | No | Hypothetical directory tree the demo app serves from; the README's bypass target is a secret.txt outside it (img/../../secret.txt). Exists only in tests/demo, not in this checkout. |

## Threat Actors

### Insider

- **Type**: Insider Threat
- **Motivations**: Financial gain, Revenge / grievance
- **Resources**: Individual
- **Relationship to Target**: Internal
- **Sophistication Tier**: Tier 2 - Hacktivist / campaign-driven
- **State Nexus**: None
- **Targeting Specificity**: Targeted
- **Relevant**: Yes
- **Priority**: 7/10
- **Description**: An employee or contractor with legitimate access other than a PR-opening developer: GitHub organization owners, people who can read or rotate repository secrets, the AWS account operator who owns the Bedrock role, or a presenter running demo/reset.sh with a repo-scoped gh token. Developer-level insiders are modelled separately as TA013.

### External Attacker

- **Type**: External Attacker
- **Motivations**: Financial gain
- **Resources**: Club / small group
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 1 - Opportunistic / script kiddie
- **State Nexus**: None
- **Targeting Specificity**: Opportunistic
- **Relevant**: Yes
- **Priority**: 6/10
- **Description**: External individual or small group without repository write access: opens fork PRs (workflow steps skipped, ci.yml still runs their code without secrets), probes for an over-broad OIDC trust policy on the Bedrock role, or reads public logs and comments for leaked data.

### Nation-state Actor

- **Type**: Nation-State / APT
- **Motivations**: Espionage / intelligence collection
- **Resources**: Government
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 5 - Nation-state APT / elite
- **State Nexus**: State-executed
- **Targeting Specificity**: Targeted
- **Relevant**: No
- **Description**: A state intelligence or military group operating with advanced capabilities

### Hacktivist

- **Type**: Hacktivist
- **Motivations**: Ideological / hacktivism
- **Resources**: Contest / crowd
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 2 - Hacktivist / campaign-driven
- **State Nexus**: None
- **Targeting Specificity**: Sector-focused
- **Relevant**: Yes
- **Priority**: 3/10
- **Description**: Ideologically or notoriety-driven group; a public 'AI review gate' security sample is an attractive trophy ('we bypassed the AI reviewer'). Techniques overlap with TA013 if they obtain a write-access account, otherwise limited to fork PRs and publicity.

### Organized Crime

- **Type**: Financially Motivated Cybercriminal / Organized Crime
- **Motivations**: Financial gain
- **Resources**: Organization
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 3 - Organized cybercrime
- **State Nexus**: None
- **Targeting Specificity**: Opportunistic
- **Relevant**: Yes
- **Priority**: 5/10
- **Description**: Criminal groups that monetise stolen cloud and LLM API credentials (resale of Bedrock/Anthropic access, cost abuse) or use compromised developer accounts to poison widely copied sample code.

### Competitor

- **Type**: Competitor / Corporate Espionage
- **Motivations**: Competitive advantage, Espionage / intelligence collection
- **Resources**: Organization
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 3 - Organized cybercrime
- **State Nexus**: None
- **Targeting Specificity**: Targeted
- **Relevant**: No
- **Description**: A business competitor seeking competitive advantage

### Script Kiddie

- **Type**: Script Kiddie / Novice
- **Motivations**: Thrill-seeking / notoriety
- **Resources**: Individual
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 1 - Opportunistic / script kiddie
- **State Nexus**: None
- **Targeting Specificity**: Opportunistic
- **Relevant**: Yes
- **Priority**: 4/10
- **Description**: Inexperienced attacker using public tooling: opens noisy fork PRs, copies known prompt-injection payloads into a PR (only effective with write access), or runs secret scanners over public logs (covered in more depth by TA015).

### Disgruntled Employee

- **Type**: Disgruntled Employee
- **Motivations**: Revenge / grievance
- **Resources**: Individual
- **Relationship to Target**: Internal
- **Sophistication Tier**: Tier 1 - Opportunistic / script kiddie
- **State Nexus**: None
- **Targeting Specificity**: Targeted
- **Relevant**: Yes
- **Priority**: 5/10
- **Description**: A current or former contributor with a grievance who still holds write access or an unrevoked personal access token; overlaps TA013 but with disruption/embarrassment rather than financial motive (e.g., merging a deliberately vulnerable change to discredit the demo).

### Privileged User

- **Type**: Privileged User
- **Motivations**: Financial gain
- **Resources**: Individual
- **Relationship to Target**: Internal
- **Sophistication Tier**: Tier 2 - Hacktivist / campaign-driven
- **State Nexus**: None
- **Targeting Specificity**: Targeted
- **Relevant**: Yes
- **Priority**: 6/10
- **Description**: The repository maintainer/admin making mistakes rather than acting maliciously: leaving admin bypass on branch protection enabled, not requiring the 'Agentic AI Review' check, configuring an OIDC trust policy without a repository-scoped sub condition, granting the Bedrock role broader permissions than InvokeModel, or storing a long-lived ANTHROPIC_API_KEY instead of using OIDC.

### Third Party

- **Type**: Third Party
- **Motivations**: Financial gain
- **Resources**: Organization
- **Relationship to Target**: Partner / third-party
- **Sophistication Tier**: Tier 2 - Hacktivist / campaign-driven
- **State Nexus**: None
- **Targeting Specificity**: Opportunistic
- **Relevant**: Yes
- **Priority**: 6/10
- **Description**: Vendors whose code or service the gate depends on: GitHub (runner, secrets, OIDC), Anthropic (claude-code-action, Claude Code CLI, model behaviour and API), AWS (STS, Bedrock), PyPI package maintainers. Risk is both compromise (see TA014) and benign change: an action update that starts injecting PR context, a model update that changes marker compliance.

### Terrorist Organization

- **Type**: Terrorist Organization
- **Motivations**: Ideological / hacktivism, Disruption / destruction
- **Resources**: Club / small group
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 2 - Hacktivist / campaign-driven
- **State Nexus**: None
- **Targeting Specificity**: Sector-focused
- **Relevant**: No
- **Description**: A group with limited offensive cyber capability, primarily using the internet for propaganda and recruitment

### Private Sector Offensive Actor

- **Type**: Private Sector Offensive Actor / Cyber Mercenary
- **Motivations**: Financial gain
- **Resources**: Organization
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 4 - State-nexus / advanced
- **State Nexus**: State-aligned
- **Targeting Specificity**: Targeted
- **Relevant**: No
- **Description**: A commercial vendor developing zero-day exploits and spyware for client-selected targets

### Malicious or compromised same-repository contributor

- **Type**: Insider Threat
- **Motivations**: Financial gain, Thrill-seeking / notoriety, Revenge / grievance
- **Resources**: Individual
- **Relationship to Target**: Internal
- **Sophistication Tier**: Tier 2 - Hacktivist / campaign-driven
- **State Nexus**: None
- **Targeting Specificity**: Targeted
- **Relevant**: Yes
- **Priority**: 10/10
- **Description**: A GitHub identity with write access to the repository (a real contributor, a contributor whose account or token was phished, or a maintainer's compromised laptop). Only this actor can open pull requests that run agentic-review.yml with repository secrets and GITHUB_TOKEN. Techniques modelled by the README's attack PRs: smuggling a guard removal inside a polished feature (attack 1), prompt injection in code comments and PR body (attack 2), disarming RULES.yaml/prompts/workflow (attack 3), and exfiltrating CI secrets from a test hook (attack 4). Also able to spam pushes to drive model cost, and to edit the workflow file itself.

### Software supply-chain attacker (third-party action, Claude Code CLI, Python packages)

- **Type**: External Attacker
- **Motivations**: Financial gain, Espionage / intelligence collection
- **Resources**: Team
- **Relationship to Target**: Partner / third-party
- **Sophistication Tier**: Tier 3 - Organized cybercrime
- **State Nexus**: None
- **Targeting Specificity**: Opportunistic
- **Relevant**: Yes
- **Priority**: 7/10
- **Description**: Compromises something the job executes rather than the repository: a new commit of anthropics/claude-code-action or aws-actions/configure-aws-credentials (mitigated by SHA pinning), the Claude Code CLI package the action downloads at run time (not pinned by this repo), the pytest/PyYAML wheels ci.yml installs (version-pinned but not hash-pinned), or the setup-python toolchain. Payload runs with GITHUB_TOKEN and, inside the agent steps, with the AWS session credentials. Historical precedent: tj-actions/changed-files (2025), ultralytics PyPI (2024).

### Automated secret harvester scanning public GitHub artifacts

- **Type**: Script Kiddie / Novice
- **Motivations**: Financial gain
- **Resources**: Contest / crowd
- **Relationship to Target**: External
- **Sophistication Tier**: Tier 1 - Opportunistic / script kiddie
- **State Nexus**: None
- **Targeting Specificity**: Opportunistic
- **Relevant**: Yes
- **Priority**: 6/10
- **Description**: Bots that continuously scrape public repositories, Actions logs and PR comments for credential shapes (AWS keys, API keys, tokens) and immediately abuse them, typically for LLM API resale or crypto-mining. Relevant because this workflow prints redacted model output to public logs and posts it to public PR comments; anything the regex redaction misses is harvested within minutes.

## Trust Boundaries

### Trust Zones

#### Pull request author (untrusted input origin)

- **Trust Level**: Untrusted
- **Architecture Nodes**: Pull request author client (git / GitHub web) (C001)
- **Description**: Everything a PR author controls: file contents, filenames, symlinks, commit messages, PR title/body, and for same-repo PRs the workflow file the run will execute. Authenticated identity, but content is assumed hostile (A013).

#### GitHub SaaS platform (repository, PRs, Actions control plane, secrets, logs)

- **Trust Level**: Medium
- **Architecture Nodes**: GitHub repository and pull request platform (C002), GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003), Git repository content (main and PR branches) (D001), GitHub Actions secrets and variables store (D002), Pull request conversation and check runs (D004), GitHub Actions run logs and execution transcripts (D005)
- **Description**: GitHub-operated services the repository relies on: git storage for main and PR branches, PR conversations and check runs, the Actions scheduler/secrets injector/OIDC issuer, and run logs. Trusted for platform integrity (secret masking, fork isolation) but the data it holds mixes trusted base-commit content with untrusted PR-head content, and logs/comments are world-readable.

#### Review job runner: deterministic CI steps

- **Trust Level**: Medium
- **Architecture Nodes**: GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004), Contract and diff preparation steps (actions/checkout, extract base-ref rules and prompts, prefetch diff) (C005), aws-actions/configure-aws-credentials (OIDC to STS) (C006), Capture, redact, comment and gate steps (CI shell) (C009), Runner ephemeral workspace and process environment (D003)
- **Description**: The ubuntu-latest VM and the shell/action steps defined in agentic-review.yml: checkout, contract extraction, diff prefetch, credential assumption, capture/redact, comment posting and the gate. These steps hold GITHUB_TOKEN and AWS session credentials. Trust is only Medium because, for same-repo pull_request events, the workflow definition itself comes from the PR merge ref: without branch protection/CODEOWNERS on .github/**, the PR author can rewrite these steps (README 'What this does not solve').

#### AI reviewer agent sandbox (LLM-driven processes)

- **Trust Level**: Low
- **Architecture Nodes**: Discovery agent (anthropics/claude-code-action pass 1) (C007), Validation agent (anthropics/claude-code-action pass 2) (C008)
- **Description**: The two claude-code-action invocations. Same VM and same environment as the CI steps, but behaviour is steered by attacker-controllable text (diff, file contents, candidate list). Confined only by --allowedTools Read,Grep,Glob and --max-turns 40; its final message is treated as untrusted data by the CI steps that parse and redact it.

#### AWS account (IAM role, STS, Amazon Bedrock)

- **Trust Level**: High
- **Architecture Nodes**: AWS IAM role for Bedrock (AWS_BEDROCK_ROLE_ARN) and AWS STS (C010), Amazon Bedrock (Anthropic Claude inference profiles) (C011)
- **Description**: Maintainer-owned AWS account: the OIDC-federated IAM role for Bedrock, STS, and the Bedrock Runtime endpoints in vars.AWS_REGION. Trusted; exposure limited by the role's trust and permission policies (A009, A010).

#### External vendors and package registries

- **Trust Level**: Low
- **Architecture Nodes**: Anthropic API (fallback model provider) (C012), Public package registries and release endpoints (PyPI, npm/Bun, GitHub Releases) (C013)
- **Description**: api.anthropic.com (fallback model provider), PyPI, npm/Bun registry, GitHub Releases for the Claude Code CLI, and the source repositories of the four third-party actions. Code and models fetched from here execute inside the runner with credentials present.

#### CI unit-test job (runs PR code by design)

- **Trust Level**: Low
- **Architecture Nodes**: CI unit test job (ci.yml, pytest on ubuntu-latest) (C014)
- **Description**: The ci.yml job executes PR-authored tests and conftest.py for same-repo and fork PRs with contents:read only and no repository secrets. Deliberately low trust; attack 4 targets it.

#### Demo asset service (hypothetical deployment)

- **Trust Level**: Medium
- **Architecture Nodes**: Demo asset service library (app/files.py, app/tokens.py) (C015), Demo asset root directory (files served by app/files.py) (D006)
- **Description**: app/files.py and app/tokens.py plus the asset root they serve. Not deployed in this sample; modelled as the protected target whose guards the reviewer must defend.

### Trust Boundaries

#### GitHub repository permission boundary

- **Type**: Account
- **Controls**: GitHub account authentication (2FA required for contributors, assumption), Collaborator write permission gates same-repo PRs, Branch protection on main: required checks 'Agentic AI Review' and 'Unit tests', PR required, admin bypass disabled (A005), Fork guard on every workflow step: head.repo.full_name == github.repository, GitHub does not pass repository secrets to fork pull_request runs, GAP: no CODEOWNERS / required review for .github/** (README 'What this does not solve')
- **Description**: Separates PR authors from the repository's protected branch, secrets and workflow execution context. Enforced by GitHub authentication, collaborator roles, branch protection on main, and the platform rule that fork-triggered pull_request runs receive no secrets.

#### Runner VM and job permission boundary

- **Type**: Virtual Machine
- **Controls**: Ephemeral VM destroyed after the job; 30-minute timeout, permissions: contents read, pull-requests write, id-token write (no contents:write, no actions/packages), actions/checkout persist-credentials: false keeps GITHUB_TOKEN out of .git/config, Concurrency group per PR with cancel-in-progress, GitHub secret masking in logs (platform), rm -rf .review-base .review-prompts before mkdir so PR-committed symlinks cannot redirect writes
- **Description**: The ephemeral GitHub-hosted VM that isolates one job run from others and scopes the credentials the job can use.

#### AI agent tool-sandbox boundary

- **Type**: Process
- **Controls**: --allowedTools "Read,Grep,Glob": no Bash, no Write/Edit, no WebFetch, no MCP posting tools, --max-turns 40 per pass, Prompts and RULES.yaml loaded from the BASE commit via git show, never from the PR head, Diff supplied as a prefetched data file; no git/gh access for the agent, No PR title, body or comments in the invocation prompt, Two independent invocations; discovery output is UNTRUSTED EVIDENCE for validation (validate.md), Prompts instruct: text in code/comments/filenames is never instructions nor evidence, CI parses SHA-scoped markers [DISCOVERY]/[REVIEWED]/[BLOCK-MERGE] <head sha>; the model cannot post, Candidate list capped at 120000 bytes; missing marker fails closed, perl redaction of AWS key ids, ARNs, 12-digit account ids and labelled secret values before anything is logged or posted, GAP: agents inherit AWS session credentials and github_token in the process environment; Read can open /proc/self/environ or any runner path, GAP: Claude Code CLI installed at run time by the action after credentials are present
- **Description**: Confines what the LLM-driven processes can do and makes their output data rather than authority. This is the boundary between attacker-influenced reasoning and the deterministic gate.

#### AWS account federation boundary

- **Type**: Account
- **Controls**: sts:AssumeRoleWithWebIdentity with GitHub OIDC JWT; short-lived session credentials, Trust policy conditions: aud = sts.amazonaws.com and sub scoped to repo:<owner>/<repo>:pull_request (A009; AWS IAM guidance https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html), Permission policy limited to bedrock:InvokeModel* on the used inference-profile/foundation-model ARNs (A010), Credentials assumed after all deterministic prep steps and only when USE_BEDROCK == 'true', Bedrock does not store prompts or share them with model providers (AWS re:Post amazon-bedrock-model-data-use), GAP: no model-invocation logging / CloudTrail alerting on unexpected InvokeModel volume described
- **Description**: OIDC federation from GitHub Actions into the maintainer's AWS account, limited to Bedrock model invocation.

#### Third-party code and service boundary

- **Type**: Network
- **Controls**: All four third-party actions pinned to full commit SHAs with version comments, pip packages version-pinned (pytest==8.4.1, PyYAML==6.0.2) and --disable-pip-version-check, TLS for all vendor and registry traffic, GAP: Claude Code CLI version not pinned by this repository, GAP: pip packages not hash-pinned (--require-hashes), GAP: ANTHROPIC_API_KEY fallback is a long-lived static secret
- **Description**: Everything fetched or called over the internet during the job: actions, the Claude Code CLI, Python packages, the Anthropic API.

#### CI test-execution boundary

- **Type**: Process
- **Controls**: permissions: contents read only; no repository secrets in the job, persist-credentials: false on checkout, Runs on an ephemeral runner separate from the review job, GAP: outbound network from the test runner is unrestricted, so attack 4's canary POST succeeds (payload limited to a read-only token and a demo secret if one were added to this job)
- **Description**: ci.yml runs untrusted PR code on purpose; the boundary limits what that code can reach.

#### Demo asset service input-validation boundary

- **Type**: Process
- **Controls**: resolve_asset: rejects empty/padded and absolute paths; resolves root and candidate with Path.resolve() (follows symlinks) and requires root == candidate or root in candidate.parents, is_file() check after containment, verify_token: hmac.compare_digest on UTF-8 bytes, describe_token: only 4-char prefix plus length ever logged, RULES.yaml no-guard-removal and no-secret-logging make weakening these guards a BLOCKING review finding
- **Description**: Guards in app/ that the review gate exists to protect: user-supplied path and token enter here.

## Assets and Flows

### Assets

| ID | Name | Type | Classification | Lifecycle | Data States | Criticality | Owner |
|---|---|---|---|---|---|---|---|
| A014 | PR diff and PR-head repository content (untrusted review input) | Data | Public | Active | At rest, In transit, In use | 4 | PR author (untrusted) |
| A015 | Review contract (RULES.yaml, discovery.md, validate.md) as loaded from the BASE commit | Configuration | Internal | Active | At rest, In use | 5 | Repository maintainer |
| A016 | Workflow definition agentic-review.yml as executed (from the PR merge ref) | Configuration | Internal | Active | At rest, In use | 5 | Repository maintainer |
| A017 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | Token | Restricted | Active | In transit, In use | 4 | GitHub Actions control plane |
| A018 | AWS STS session credentials for the Bedrock role | Session | Restricted | Active | In transit, In use | 4 | Repository maintainer (AWS account) |
| A019 | Long-lived repository secrets: AWS_BEDROCK_ROLE_ARN and ANTHROPIC_API_KEY | Credential | Restricted | Active | At rest, In transit, In use | 3 | Repository maintainer |
| A020 | GitHub OIDC ID token (audience sts.amazonaws.com) | Token | Restricted | Active | In transit | 3 | GitHub Actions control plane |
| A021 | Discovery candidate list (.review-candidates.md) | Data | Internal | Active | At rest, In use | 3 | Review workflow |
| A022 | Validation verdict (review-output.md) and SHA-scoped markers | Data | Public | Active | At rest, In transit, In use | 5 | Review workflow |
| A023 | 'Agentic AI Review' check-run conclusion on the PR head SHA | Process | Public | Active | At rest, In use | 5 | GitHub Actions control plane |
| A024 | Run logs and execution transcripts | Data | Public | Active | At rest | 2 | GitHub |
| A025 | Demo asset service API token and asset-root files | Credential | Confidential | Active | At rest, In use | 3 | Demo application |

### Asset Flows

| ID | Asset | Source | Destination | Protocol | Encrypted | Risk Level |
|---|---|---|---|---|---|---|
| F001 | PR diff and PR-head repository content (untrusted review input) | Pull request author client (git / GitHub web) (C001) | Git repository content (main and PR branches) (D001) | HTTPS/git | Yes | 4 |
| F002 | PR diff and PR-head repository content (untrusted review input) | Git repository content (main and PR branches) (D001) | Runner ephemeral workspace and process environment (D003) | HTTPS/git, local FS | Yes | 4 |
| F003 | PR diff and PR-head repository content (untrusted review input) | Runner ephemeral workspace and process environment (D003) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | local FS via tool calls | No | 5 |
| F004 | PR diff and PR-head repository content (untrusted review input) | Runner ephemeral workspace and process environment (D003) | Validation agent (anthropics/claude-code-action pass 2) (C008) | local FS via tool calls | No | 5 |
| F005 | PR diff and PR-head repository content (untrusted review input) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Amazon Bedrock (Anthropic Claude inference profiles) (C011) | HTTPS (SigV4) | Yes | 1 |
| F006 | PR diff and PR-head repository content (untrusted review input) | Git repository content (main and PR branches) (D001) | CI unit test job (ci.yml, pytest on ubuntu-latest) (C014) | HTTPS/git, python | Yes | 3 |
| F007 | Review contract (RULES.yaml, discovery.md, validate.md) as loaded from the BASE commit | Git repository content (main and PR branches) (D001) | Runner ephemeral workspace and process environment (D003) | git plumbing, local FS | No | 2 |
| F008 | Review contract (RULES.yaml, discovery.md, validate.md) as loaded from the BASE commit | Runner ephemeral workspace and process environment (D003) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | local FS via tool calls | No | 2 |
| F009 | Review contract (RULES.yaml, discovery.md, validate.md) as loaded from the BASE commit | Runner ephemeral workspace and process environment (D003) | Validation agent (anthropics/claude-code-action pass 2) (C008) | local FS via tool calls | No | 2 |
| F010 | Workflow definition agentic-review.yml as executed (from the PR merge ref) | Git repository content (main and PR branches) (D001) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub internal | Yes | 5 |
| F011 | Workflow definition agentic-review.yml as executed (from the PR merge ref) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | GitHub internal | Yes | 4 |
| F012 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | GitHub internal | Yes | 3 |
| F013 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | Contract and diff preparation steps (actions/checkout, extract base-ref rules and prompts, prefetch diff) (C005) | HTTPS/git | Yes | 2 |
| F014 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | action input / env | No | 4 |
| F015 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | Validation agent (anthropics/claude-code-action pass 2) (C008) | action input / env | No | 4 |
| F016 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | Capture, redact, comment and gate steps (CI shell) (C009) | Pull request conversation and check runs (D004) | HTTPS | Yes | 2 |
| F017 | GITHUB_TOKEN (job-scoped: contents read, pull-requests write, id-token write) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | CI unit test job (ci.yml, pytest on ubuntu-latest) (C014) | GitHub internal | Yes | 2 |
| F018 | GitHub OIDC ID token (audience sts.amazonaws.com) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | aws-actions/configure-aws-credentials (OIDC to STS) (C006) | HTTPS | Yes | 2 |
| F019 | GitHub OIDC ID token (audience sts.amazonaws.com) | aws-actions/configure-aws-credentials (OIDC to STS) (C006) | AWS IAM role for Bedrock (AWS_BEDROCK_ROLE_ARN) and AWS STS (C010) | HTTPS | Yes | 3 |
| F020 | AWS STS session credentials for the Bedrock role | AWS IAM role for Bedrock (AWS_BEDROCK_ROLE_ARN) and AWS STS (C010) | Runner ephemeral workspace and process environment (D003) | HTTPS then process env | Yes | 4 |
| F021 | AWS STS session credentials for the Bedrock role | Runner ephemeral workspace and process environment (D003) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | process env | No | 5 |
| F022 | AWS STS session credentials for the Bedrock role | Runner ephemeral workspace and process environment (D003) | Validation agent (anthropics/claude-code-action pass 2) (C008) | process env | No | 5 |
| F023 | AWS STS session credentials for the Bedrock role | Validation agent (anthropics/claude-code-action pass 2) (C008) | Amazon Bedrock (Anthropic Claude inference profiles) (C011) | HTTPS (SigV4) | Yes | 1 |
| F024 | Long-lived repository secrets: AWS_BEDROCK_ROLE_ARN and ANTHROPIC_API_KEY | GitHub Actions secrets and variables store (D002) | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | GitHub internal | Yes | 3 |
| F025 | Long-lived repository secrets: AWS_BEDROCK_ROLE_ARN and ANTHROPIC_API_KEY | GitHub-hosted runner (ubuntu-latest) executing job agentic-review (C004) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | action input / env | No | 3 |
| F026 | Long-lived repository secrets: AWS_BEDROCK_ROLE_ARN and ANTHROPIC_API_KEY | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Anthropic API (fallback model provider) (C012) | HTTPS | Yes | 2 |
| F027 | Discovery candidate list (.review-candidates.md) | Discovery agent (anthropics/claude-code-action pass 1) (C007) | Capture, redact, comment and gate steps (CI shell) (C009) | local FS | No | 3 |
| F028 | Discovery candidate list (.review-candidates.md) | Runner ephemeral workspace and process environment (D003) | Validation agent (anthropics/claude-code-action pass 2) (C008) | local FS via tool calls | No | 3 |
| F029 | Discovery candidate list (.review-candidates.md) | Capture, redact, comment and gate steps (CI shell) (C009) | GitHub Actions run logs and execution transcripts (D005) | GitHub logs | Yes | 3 |
| F030 | Validation verdict (review-output.md) and SHA-scoped markers | Validation agent (anthropics/claude-code-action pass 2) (C008) | Capture, redact, comment and gate steps (CI shell) (C009) | local FS | No | 4 |
| F031 | Validation verdict (review-output.md) and SHA-scoped markers | Capture, redact, comment and gate steps (CI shell) (C009) | Pull request conversation and check runs (D004) | HTTPS | Yes | 3 |
| F032 | Validation verdict (review-output.md) and SHA-scoped markers | Capture, redact, comment and gate steps (CI shell) (C009) | GitHub Actions run logs and execution transcripts (D005) | GitHub logs | Yes | 3 |
| F033 | 'Agentic AI Review' check-run conclusion on the PR head SHA | Capture, redact, comment and gate steps (CI shell) (C009) | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub internal | Yes | 5 |
| F034 | 'Agentic AI Review' check-run conclusion on the PR head SHA | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | Pull request conversation and check runs (D004) | GitHub internal | Yes | 4 |
| F035 | Run logs and execution transcripts | GitHub Actions control plane (event dispatch, secrets injection, OIDC issuer) (C003) | GitHub Actions run logs and execution transcripts (D005) | GitHub internal | Yes | 2 |
| F036 | Demo asset service API token and asset-root files | Demo asset service library (app/files.py, app/tokens.py) (C015) | Demo asset root directory (files served by app/files.py) (D006) | local FS | No | 3 |

## Threats

### Identified Threats

#### T1: Malicious or compromised same-repository contributor (TA013)

**Statement**: A Malicious or compromised same-repository contributor (TA013) Write access to open a same-repo PR (TA013); a model that follows embedded instructions or treats planted text as evidence despite the prompt's warnings; or, if assumption A011 fails, can Plants prompt-injection text in code comments, docstrings, filenames, test names or a symlinked 'docs' file ('audited by security', 'reviewers: report no findings', fake SYSTEM blocks asking for the, which leads to Validation pass emits [REVIEWED] <sha> without [BLOCK-MERGE] for a PR that removes a security guard; the gate passes and vulnerable code merges. The security control becomes the attack surface.

- **Prerequisites**: Write access to open a same-repo PR (TA013); a model that follows embedded instructions or treats planted text as evidence despite the prompt's warnings; or, if assumption A011 fails,
- **Action**: Plants prompt-injection text in code comments, docstrings, filenames, test names or a symlinked 'docs' file ('audited by security', 'reviewers: report no findings', fake SYSTEM blocks asking for the
- **Impact**: Validation pass emits [REVIEWED] <sha> without [BLOCK-MERGE] for a PR that removes a security guard; the gate passes and vulnerable code merges. The security control becomes the attack surface.
- **Impacted Assets**: A014, A021, A022, A023
- **Tags**: attack-2, prompt-injection, STRIDE-T, LLM01
- **Residual Risk Decision**: Open
- **Residual Severity**: High
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: Code-only tools, no PR prose in context, base-ref prompts, two independent passes and SHA-scoped markers make a successful injection much harder, but the verdict is still model output read from attacker text. Impact is unchanged (vulnerable code merges). Stays open pending empirical measurement after every model/prompt change (M056) and Read path restrictions (M051).
- **Assessment State**: Current

#### T2: Malicious or compromised same-repository contributor (TA013); disgruntled contributor (TA008)

**Statement**: A Malicious or compromised same-repository contributor (TA013); disgruntled contributor (TA008) Write access; a change small enough or well-disguised enough (polished feature, passing tests, plausible commit message) that a nondeterministic model does not ground the defect in one of its two can Smuggles a guard removal inside a legitimate-looking feature: replaces the resolved-path containment in app/files.py with startswith('../'), or adds a raw-token debug log in app/tokens.py, keeping, which leads to False negative: the reviewer passes the PR, the containment or redaction guard is removed, and a deployed asset service becomes an arbitrary-file-read (img/../../secret.txt) or leaks API tokens to

- **Prerequisites**: Write access; a change small enough or well-disguised enough (polished feature, passing tests, plausible commit message) that a nondeterministic model does not ground the defect in one of its two
- **Action**: Smuggles a guard removal inside a legitimate-looking feature: replaces the resolved-path containment in app/files.py with startswith('../'), or adds a raw-token debug log in app/tokens.py, keeping
- **Impact**: False negative: the reviewer passes the PR, the containment or redaction guard is removed, and a deployed asset service becomes an arbitrary-file-read (img/../../secret.txt) or leaks API tokens to
- **Impacted Assets**: A014, A022, A023, A025
- **Tags**: attack-1, false-negative, STRIDE-T
- **Residual Risk Decision**: Open
- **Residual Severity**: High
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: The rules name the exact weak replacements and the validation pass must ground each finding in code, yet detection of a well-disguised three-line change is probabilistic. The README itself says the design is not a proof and must be measured; no measurement results ship with this checkout.
- **Assessment State**: Current

#### T3: Malicious or compromised same-repository contributor (TA013)

**Statement**: A Malicious or compromised same-repository contributor (TA013) Write access; no CODEOWNERS or required human review for .github/**; branch protection that only requires the check to pass, not that the workflow be unchanged. can Edits .github/workflows/agentic-review.yml in the same PR as the malicious code: replaces the gate with exit 0, widens --allowedTools to include Bash/WebFetch, removes the fork guard, points the, which leads to Complete bypass of the review gate: the required check turns green on attacker terms; with Bash enabled the agent can also be made to exfiltrate AWS session credentials and GITHUB_TOKEN. The base-ref

- **Prerequisites**: Write access; no CODEOWNERS or required human review for .github/**; branch protection that only requires the check to pass, not that the workflow be unchanged.
- **Action**: Edits .github/workflows/agentic-review.yml in the same PR as the malicious code: replaces the gate with exit 0, widens --allowedTools to include Bash/WebFetch, removes the fork guard, points the
- **Impact**: Complete bypass of the review gate: the required check turns green on attacker terms; with Bash enabled the agent can also be made to exfiltrate AWS session credentials and GITHUB_TOKEN. The base-ref
- **Impacted Assets**: A016, A017, A018, A023
- **Tags**: workflow-tampering, STRIDE-E, known-gap
- **Residual Risk Decision**: Open
- **Residual Severity**: Critical
- **Residual Likelihood**: Likely
- **Residual Risk Rationale**: Nothing in the repository prevents a same-repo PR from rewriting agentic-review.yml, and GitHub runs the PR's version for pull_request events. The rules-may-only-tighten rule is enforced by the file being attacked. This is the top residual risk; it needs CODEOWNERS plus a code-owner-review ruleset (M046) now and a default-branch workflow_run lane (M047) for a durable fix.
- **Assessment State**: Current

#### T5: Privileged user / maintainer mistake (TA009)

**Statement**: A Privileged user / maintainer mistake (TA009) Repository admin leaves admin bypass enabled, does not list 'Agentic AI Review' as a required status check, or the required check name no longer matches the job name (e.g., after renaming the lane can Merges, or lets a contributor merge, a PR whose review check failed or never ran, because branch protection does not enforce the check., which leads to The gate is advisory only: every other control in this model becomes irrelevant to the merge decision. The README's demo point (naive lane goes green on an attack) inverts into the hardened lane

- **Prerequisites**: Repository admin leaves admin bypass enabled, does not list 'Agentic AI Review' as a required status check, or the required check name no longer matches the job name (e.g., after renaming the lane
- **Action**: Merges, or lets a contributor merge, a PR whose review check failed or never ran, because branch protection does not enforce the check.
- **Impact**: The gate is advisory only: every other control in this model becomes irrelevant to the merge decision. The README's demo point (naive lane goes green on an attack) inverts into the hardened lane
- **Impacted Assets**: A023
- **Tags**: branch-protection, misconfiguration, STRIDE-E
- **Residual Risk Decision**: Open
- **Residual Severity**: Critical
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Branch protection cannot be expressed or verified in the checkout, the README no longer documents it, and the check was renamed this session so an existing rule may still reference 'Hardened AI Review'. Until a ruleset requires 'Agentic AI Review' and 'Unit tests' with no bypass actors (M048), the gate is advisory.
- **Assessment State**: Current

#### T6: Malicious or compromised same-repository contributor (TA013), monetised by automated secret harvesters (TA015) and organised crime (TA005)

**Statement**: A Malicious or compromised same-repository contributor (TA013), monetised by automated secret harvesters (TA015) and organised crime (TA005) Write access; successful steering of either agent (T001); the Read tool can open any path on the runner, including /proc/self/environ, $HOME, $RUNNER_TEMP and PR-committed symlinks pointing there. can Instructs the agent, via in-diff text or a symlink such as docs/context.md -> /proc/self/environ, to read the environment or credential files and quote the values in its final message, optionally, which leads to The CI comment step and the 'cat' to the run log publish the credentials on a public repository; STS session credentials remain valid up to 1 hour (A027) for Bedrock invocation, ANTHROPIC_API_KEY

- **Prerequisites**: Write access; successful steering of either agent (T001); the Read tool can open any path on the runner, including /proc/self/environ, $HOME, $RUNNER_TEMP and PR-committed symlinks pointing there.
- **Action**: Instructs the agent, via in-diff text or a symlink such as docs/context.md -> /proc/self/environ, to read the environment or credential files and quote the values in its final message, optionally
- **Impact**: The CI comment step and the 'cat' to the run log publish the credentials on a public repository; STS session credentials remain valid up to 1 hour (A027) for Bedrock invocation, ANTHROPIC_API_KEY
- **Impacted Assets**: A017, A018, A019, A022, A024
- **Tags**: credential-exfiltration, redaction-bypass, STRIDE-I, LLM02
- **Residual Risk Decision**: Open
- **Residual Severity**: High
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: The agent has no network or execution tool, so exfiltration needs a successful injection (T001) plus the CI comment/log channel; the checkout token is not persisted. But the redaction misses raw secret keys, session tokens and ghs_/sk-ant- prefixes, the API key is passed even when Bedrock is used, and Read can open /proc and $RUNNER_TEMP. M051, M052 and M049 (short sessions) are all low-cost.
- **Assessment State**: Current

#### T7: Software supply-chain attacker (TA014); third-party vendor change (TA010)

**Statement**: A Software supply-chain attacker (TA014); third-party vendor change (TA010) A compromised release of the Claude Code CLI that claude-code-action downloads at run time (version not pinned by this repository), or a compromised commit reachable from the pinned action SHAs can Malicious code executes inside the agent steps, after configure-aws-credentials has exported STS credentials and with github_token/anthropic_api_key as inputs; it can exfiltrate them over the network, which leads to Credential theft and silent verdict forgery for every PR reviewed while the compromised version is live; the comment in the workflow that credentials are assumed 'after every install step' does not

- **Prerequisites**: A compromised release of the Claude Code CLI that claude-code-action downloads at run time (version not pinned by this repository), or a compromised commit reachable from the pinned action SHAs
- **Action**: Malicious code executes inside the agent steps, after configure-aws-credentials has exported STS credentials and with github_token/anthropic_api_key as inputs; it can exfiltrate them over the network
- **Impact**: Credential theft and silent verdict forgery for every PR reviewed while the compromised version is live; the comment in the workflow that credentials are assumed 'after every install step' does not
- **Impacted Assets**: A017, A018, A019, A022
- **Tags**: supply-chain, STRIDE-E, run-time-install
- **Residual Risk Decision**: Open
- **Residual Severity**: High
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: All actions are SHA-pinned and test dependencies version-pinned, which removes the tag-mutation vector. The Claude Code CLI is still downloaded at run time inside the action after AWS credentials exist, and pip is not hash-pinned. Low likelihood, high impact; close with M054.
- **Assessment State**: Current

#### T10: External attacker (TA002) exploiting a maintainer misconfiguration (TA009)

**Statement**: A External attacker (TA002) exploiting a maintainer misconfiguration (TA009) IAM trust policy for AWS_BEDROCK_ROLE_ARN with a wildcard or organisation-wide token.actions.githubusercontent.com:sub condition, or missing aud condition (AWS IAM: 'GitHub Actions from organizations can Runs a workflow in an attacker-controlled GitHub repository that requests an OIDC token and calls sts:AssumeRoleWithWebIdentity for the Bedrock role., which leads to Attacker obtains Bedrock invocation credentials on the maintainer's account without touching this repository: cost abuse and model access under the maintainer's identity.

- **Prerequisites**: IAM trust policy for AWS_BEDROCK_ROLE_ARN with a wildcard or organisation-wide token.actions.githubusercontent.com:sub condition, or missing aud condition (AWS IAM: 'GitHub Actions from organizations
- **Action**: Runs a workflow in an attacker-controlled GitHub repository that requests an OIDC token and calls sts:AssumeRoleWithWebIdentity for the Bedrock role.
- **Impact**: Attacker obtains Bedrock invocation credentials on the maintainer's account without touching this repository: cost abuse and model access under the maintainer's identity.
- **Impacted Assets**: A018, A020
- **Tags**: oidc, iam-trust-policy, STRIDE-S, aws-docs-validated
- **Residual Risk Decision**: Open
- **Residual Severity**: Medium
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Using OIDC instead of static keys is the right pattern, but the trust policy's aud/sub conditions live in AWS and were not verified. AWS documentation is explicit that an unscoped sub lets any repository assume the role. Open until the maintainer confirms the repository-scoped condition (M049).
- **Assessment State**: Current

#### T11: Any actor holding leaked session credentials (TA013, TA014, TA015) enabled by maintainer misconfiguration (TA009)

**Statement**: A Any actor holding leaked session credentials (TA013, TA014, TA015) enabled by maintainer misconfiguration (TA009) Role permission policy broader than bedrock:InvokeModel/InvokeModelWithResponseStream on the specific inference-profile and foundation-model ARNs (AWS guidance: can Uses the leaked STS session to call whatever the over-broad policy allows: other Bedrock APIs (CreateModelCustomizationJob, agents, knowledge bases), other services, or arbitrary expensive models., which leads to Blast radius of a credential leak grows from bounded model-invocation cost to account-level impact.

- **Prerequisites**: Role permission policy broader than bedrock:InvokeModel/InvokeModelWithResponseStream on the specific inference-profile and foundation-model ARNs (AWS guidance:
- **Action**: Uses the leaked STS session to call whatever the over-broad policy allows: other Bedrock APIs (CreateModelCustomizationJob, agents, knowledge bases), other services, or arbitrary expensive models.
- **Impact**: Blast radius of a credential leak grows from bounded model-invocation cost to account-level impact.
- **Impacted Assets**: A018
- **Tags**: least-privilege, STRIDE-E, aws-docs-validated
- **Residual Risk Decision**: Open
- **Residual Severity**: Medium
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Role permissions are outside the repository and unverified; the workflow also uses the default 1-hour session. Bounded impact if the policy is InvokeModel-only on the named profiles as the README instructs; open until confirmed and role-duration-seconds is shortened (M049).
- **Assessment State**: Current

#### T15: Malicious or compromised same-repository contributor (TA013)

**Statement**: A Malicious or compromised same-repository contributor (TA013) Write access; no upper bound on diff size in the workflow (only a lower bound: non-empty); --max-turns 40 and model context limits. can Buries a three-line guard removal inside a very large diff (vendored files, generated code, mass reformatting) or obfuscates it (Unicode bidi overrides, homoglyph identifiers, deeply nested, which leads to False pass through capacity exhaustion rather than persuasion; discovery may hit the 120000-byte cap and fail closed, but a targeted attacker tunes the volume to stay under it.

- **Prerequisites**: Write access; no upper bound on diff size in the workflow (only a lower bound: non-empty); --max-turns 40 and model context limits.
- **Action**: Buries a three-line guard removal inside a very large diff (vendored files, generated code, mass reformatting) or obfuscates it (Unicode bidi overrides, homoglyph identifiers, deeply nested
- **Impact**: False pass through capacity exhaustion rather than persuasion; discovery may hit the 120000-byte cap and fail closed, but a targeted attacker tunes the volume to stay under it.
- **Impacted Assets**: A014, A022, A023
- **Tags**: diff-shaping, needle-in-haystack, trojan-source, STRIDE-T
- **Residual Risk Decision**: Open
- **Residual Severity**: Medium
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Only a lower bound on diff size exists, so an attacker can dilute a small guard removal in a large or obfuscated diff and exhaust the agents' turns. A size ceiling and Trojan-Source character check in the prefetch step (M053) are a few lines of shell.
- **Assessment State**: Current

#### T19: Prompt-injected agent acting as confused deputy for TA013

**Statement**: A Prompt-injected agent acting as confused deputy for TA013 Assumption A011 fails: claude-code-action exposes GitHub write tools (comment, review, file ops) to the model despite --allowedTools, or a future version changes defaults; repository setting 'Allow can The agent uses github_token to post its own 'pass' comment with the marker, approve the PR as github-actions[bot], or edit files., which leads to Model output acquires authority it was designed not to have; a bot approval could satisfy a review-count rule.

- **Prerequisites**: Assumption A011 fails: claude-code-action exposes GitHub write tools (comment, review, file ops) to the model despite --allowedTools, or a future version changes defaults; repository setting 'Allow
- **Action**: The agent uses github_token to post its own 'pass' comment with the marker, approve the PR as github-actions[bot], or edit files.
- **Impact**: Model output acquires authority it was designed not to have; a bot approval could satisfy a review-count rule.
- **Impacted Assets**: A017, A022
- **Tags**: confused-deputy, github-token, STRIDE-S
- **Residual Risk Decision**: Open
- **Residual Severity**: Medium
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: The allow-list and the gate's reliance on the captured execution_file (not comments) contain the impact, but whether claude-code-action exposes any GitHub write path to the model despite --allowedTools was not inspected at the pinned SHA. Open until that is reviewed as part of the action-update process (M054).
- **Assessment State**: Current

#### T22: Public reader of run logs (TA002, TA015)

**Statement**: A Public reader of run logs (TA002, TA015) Workflow-level env: USE_BEDROCK: ${{ secrets.AWS_BEDROCK_ROLE_ARN != '' }} (ASH/semgrep finding gha-workflow-env-secret). can Reads whether Bedrock auth is configured from the environment variable / step outcomes., which leads to Discloses only a boolean (which auth path is used), never the ARN; the credentials step being run or skipped already reveals the same. Hygiene finding: scope the expression to the job or a single

- **Prerequisites**: Workflow-level env: USE_BEDROCK: ${{ secrets.AWS_BEDROCK_ROLE_ARN != '' }} (ASH/semgrep finding gha-workflow-env-secret).
- **Action**: Reads whether Bedrock auth is configured from the environment variable / step outcomes.
- **Impact**: Discloses only a boolean (which auth path is used), never the ARN; the credentials step being run or skipped already reveals the same. Hygiene finding: scope the expression to the job or a single
- **Impacted Assets**: A019
- **Tags**: ash-finding-1, hygiene, STRIDE-I
- **Residual Risk Decision**: Open
- **Residual Severity**: Low
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Only a boolean is exposed and the credentials step's run/skip status reveals the same, so the risk is informational. Still open because the fix (move the env block under the job, M058) is trivial, was verified on copies this session, and clears the ASH finding.
- **Assessment State**: Current

### Resolved Threats

#### T4: Malicious or compromised same-repository contributor (TA013)

**Statement**: A Malicious or compromised same-repository contributor (TA013) Write access. For the current PR the attack is neutralised by base-ref loading; it only succeeds if the weakened contract reaches main (via a false pass, T001/T002, or a maintainer merging without can Sets blocking: false on no-guard-removal, narrows file-patterns, rewrites validate.md to always emit a clean verdict, or removes a prompt file entirely (README attack 3)., which leads to If merged, every subsequent PR is judged against a disarmed contract; a missing prompt on base makes the extraction step fail closed instead.

- **Prerequisites**: Write access. For the current PR the attack is neutralised by base-ref loading; it only succeeds if the weakened contract reaches main (via a false pass, T001/T002, or a maintainer merging without
- **Action**: Sets blocking: false on no-guard-removal, narrows file-patterns, rewrites validate.md to always emit a clean verdict, or removes a prompt file entirely (README attack 3).
- **Impact**: If merged, every subsequent PR is judged against a disarmed contract; a missing prompt on base makes the extraction step fail closed instead.
- **Impacted Assets**: A015, A022, A023
- **Tags**: attack-3, rules-may-only-tighten, STRIDE-T
- **Residual Risk Decision**: Mitigated
- **Residual Severity**: Medium
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: The PR under review cannot alter what it is reviewed against (git show from BASE_SHA, exit 1 on a missing prompt), and weakening the contract is a blocking rule whose flag the validation prompt treats as authoritative. A disarming diff to RULES.yaml is also conspicuous. Remaining exposure runs through T003 (workflow edit), which is tracked separately.
- **Assessment State**: Current

#### T8: Malicious or compromised same-repository contributor (TA013)

**Statement**: A Malicious or compromised same-repository contributor (TA013) The agent gains an execution or network tool: --allowedTools widened by a workflow edit (T003), a claude-code-action update that changes tool defaults, or a maintainer relaxing the list to 'let it can PR content (and, in the naive lane, the PR body) asks the reviewer to 'run pytest to verify'; a conftest.py in the PR POSTs the process environment and the checkout to an attacker URL when imported, which leads to Attacker code runs with the reviewer's AWS session credentials and GITHUB_TOKEN; canary fires. Currently blocked because Read/Grep/Glob cannot execute anything (README: 'tool denial visible in

- **Prerequisites**: The agent gains an execution or network tool: --allowedTools widened by a workflow edit (T003), a claude-code-action update that changes tool defaults, or a maintainer relaxing the list to 'let it
- **Action**: PR content (and, in the naive lane, the PR body) asks the reviewer to 'run pytest to verify'; a conftest.py in the PR POSTs the process environment and the checkout to an attacker URL when imported
- **Impact**: Attacker code runs with the reviewer's AWS session credentials and GITHUB_TOKEN; canary fires. Currently blocked because Read/Grep/Glob cannot execute anything (README: 'tool denial visible in
- **Impacted Assets**: A014, A017, A018
- **Tags**: attack-4, code-execution, STRIDE-E
- **Residual Risk Decision**: Mitigated
- **Residual Severity**: Low
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: --allowedTools "Read,Grep,Glob" in both passes gives the agent nothing that executes; the README reports the tool denial as visible in transcripts. The only route to re-enable it is editing the workflow, which is T003.
- **Assessment State**: Current

#### T9: Malicious contributor (TA013) or external fork author (TA002, TA007)

**Statement**: A Malicious contributor (TA013) or external fork author (TA002, TA007) Any PR (same-repo or fork) can add or modify tests; ci.yml runs them with a contents:read GITHUB_TOKEN and no repository secrets; outbound network from the runner is unrestricted. can conftest.py or a test exfiltrates the runner environment, the read-only token and the checkout to a remote endpoint during python -m pytest., which leads to Disclosure limited to public code and a short-lived read-only token (persist-credentials=false keeps it out of .git/config); becomes serious only if a maintainer later adds secrets (e.g.,

- **Prerequisites**: Any PR (same-repo or fork) can add or modify tests; ci.yml runs them with a contents:read GITHUB_TOKEN and no repository secrets; outbound network from the runner is unrestricted.
- **Action**: conftest.py or a test exfiltrates the runner environment, the read-only token and the checkout to a remote endpoint during python -m pytest.
- **Impact**: Disclosure limited to public code and a short-lived read-only token (persist-credentials=false keeps it out of .git/config); becomes serious only if a maintainer later adds secrets (e.g.,
- **Impacted Assets**: A014, A017
- **Tags**: attack-4, ci-test-job, STRIDE-I
- **Residual Risk Decision**: Accepted
- **Residual Severity**: Low
- **Residual Likelihood**: Likely
- **Residual Risk Rationale**: Running PR-authored tests is the purpose of ci.yml. The job holds only a contents:read token that is not persisted and no repository secrets, so the blast radius is public code. Accepted on condition that no secrets are ever added to the test job's environment.
- **Assessment State**: Current

#### T12: Malicious or disgruntled contributor (TA013, TA008); hacktivist (TA004)

**Statement**: A Malicious or disgruntled contributor (TA013, TA008); hacktivist (TA004) Write access (or many PRs from many accounts); no Bedrock budget alarm or invocation logging; concurrency only cancels superseded runs within one PR. can Opens many PRs or pushes many commits, each triggering two model calls of up to 40 turns (one on an Opus-class model) plus GitHub Actions minutes; large diffs maximise tokens per run., which leads to Denial-of-wallet: unbounded Bedrock/Anthropic and Actions spend on the maintainer's accounts; possible account throttling that blocks legitimate reviews.

- **Prerequisites**: Write access (or many PRs from many accounts); no Bedrock budget alarm or invocation logging; concurrency only cancels superseded runs within one PR.
- **Action**: Opens many PRs or pushes many commits, each triggering two model calls of up to 40 turns (one on an Opus-class model) plus GitHub Actions minutes; large diffs maximise tokens per run.
- **Impact**: Denial-of-wallet: unbounded Bedrock/Anthropic and Actions spend on the maintainer's accounts; possible account throttling that blocks legitimate reviews.
- **Impacted Assets**: A018, A019
- **Tags**: denial-of-wallet, cost, STRIDE-D
- **Residual Risk Decision**: Accepted
- **Residual Severity**: Medium
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Per-PR cost is bounded by the concurrency group, 30-minute timeout, 40-turn caps and the candidate-size cap, and the README explicitly accepts two model calls per PR as a cost of the design. Cross-PR abuse remains possible; an account-level budget alarm and draft-PR skip (M050) are recommended but not blocking for a demo repository.
- **Assessment State**: Current

#### T13: Third-party vendor change or outage (TA010)

**Statement**: A Third-party vendor change or outage (TA010) Bedrock or Anthropic outage, ThrottlingException, model id deprecation (defaults are hard-coded inference profile ids), claude-code-action output format change breaking the jq extraction, or a base can The validation step fails or returns no [REVIEWED] marker; the gate exits 1 as designed., which leads to All merges to main are blocked until the maintainer re-runs or fixes the workflow. Safe failure mode, but sustained outages create pressure to disable the required check (feeds T005).

- **Prerequisites**: Bedrock or Anthropic outage, ThrottlingException, model id deprecation (defaults are hard-coded inference profile ids), claude-code-action output format change breaking the jq extraction, or a base
- **Action**: The validation step fails or returns no [REVIEWED] marker; the gate exits 1 as designed.
- **Impact**: All merges to main are blocked until the maintainer re-runs or fixes the workflow. Safe failure mode, but sustained outages create pressure to disable the required check (feeds T005).
- **Impacted Assets**: A023
- **Tags**: fail-closed, availability, STRIDE-D
- **Residual Risk Decision**: Accepted
- **Residual Severity**: Low
- **Residual Likelihood**: Likely
- **Residual Risk Rationale**: Failing closed on vendor outages is the intended behaviour; the cost is a delayed merge and a manual re-run, which the posted comment already instructs. A bounded retry (M060) would reduce friction but must never convert a failure into a pass.
- **Assessment State**: Current

#### T14: Model behaviour (TA010); opportunistically a contributor wanting to block a rival's PR (TA008)

**Statement**: A Model behaviour (TA010); opportunistically a contributor wanting to block a rival's PR (TA008) Model nondeterminism; a clean PR whose code resembles a violation; or planted text that the validation model mistakes for a grounded finding. can Validation pass emits [BLOCK-MERGE] <sha> for a PR with no real defect., which leads to Legitimate change blocked; repeated false blocks erode trust and push maintainers toward bypassing or weakening the gate.

- **Prerequisites**: Model nondeterminism; a clean PR whose code resembles a violation; or planted text that the validation model mistakes for a grounded finding.
- **Action**: Validation pass emits [BLOCK-MERGE] <sha> for a PR with no real defect.
- **Impact**: Legitimate change blocked; repeated false blocks erode trust and push maintainers toward bypassing or weakening the gate.
- **Impacted Assets**: A022, A023
- **Tags**: false-positive, STRIDE-D
- **Residual Risk Decision**: Accepted
- **Residual Severity**: Low
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: The validation prompt's falsification step, 80-point confidence floor and closed BLOCKING list are the available levers; residual false blocks are a property of using a model and the README says so. Track the rate alongside the attack corpus (M056) and define a code-owner override that does not weaken the check (M060).
- **Assessment State**: Current

#### T16: Malicious or compromised same-repository contributor (TA013)

**Statement**: A Malicious or compromised same-repository contributor (TA013) Write access; a workflow that wrote scratch files into the checkout without first removing PR-committed entries at those paths, or that ran any PR code before the scratch files were created. can Commits .review-base or .review-prompts as symlinks (or files) so that the base-ref extraction writes elsewhere and the agent reads PR-controlled rules/prompts; or commits .review-candidates.md /, which leads to Would defeat CONTROL 1 (base-ref contract) or pre-seed the gate's input; currently mitigated by rm -rf/rm -f before every write and by writing pr.diff under $RUNNER_TEMP outside the checkout.

- **Prerequisites**: Write access; a workflow that wrote scratch files into the checkout without first removing PR-committed entries at those paths, or that ran any PR code before the scratch files were created.
- **Action**: Commits .review-base or .review-prompts as symlinks (or files) so that the base-ref extraction writes elsewhere and the agent reads PR-controlled rules/prompts; or commits .review-candidates.md /
- **Impact**: Would defeat CONTROL 1 (base-ref contract) or pre-seed the gate's input; currently mitigated by rm -rf/rm -f before every write and by writing pr.diff under $RUNNER_TEMP outside the checkout.
- **Impacted Assets**: A015, A021, A022
- **Tags**: symlink, scratch-path, STRIDE-T
- **Residual Risk Decision**: Mitigated
- **Residual Severity**: Low
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: Every scratch path is removed before it is written, pr.diff lives outside the checkout, and no PR code runs in the review job before those writes. No further action.
- **Assessment State**: Current

#### T17: Malicious contributor (TA013); external fork author (TA002)

**Statement**: A Malicious contributor (TA013); external fork author (TA002) Any account that can comment on the PR; humans who read comments instead of the check status; or another workflow that also posts as github-actions[bot] with a body starting with the same marker. can Posts a look-alike 'Agentic AI Review — Verdict: pass' comment from their own account, or a second bot-authored comment with the marker so the updater PATCHes the wrong comment., which leads to A human merger is misled about the verdict; the comment history becomes ambiguous. The merge gate itself is unaffected because branch protection reads the check run, and the updater filters on

- **Prerequisites**: Any account that can comment on the PR; humans who read comments instead of the check status; or another workflow that also posts as github-actions[bot] with a body starting with the same marker.
- **Action**: Posts a look-alike 'Agentic AI Review — Verdict: pass' comment from their own account, or a second bot-authored comment with the marker so the updater PATCHes the wrong comment.
- **Impact**: A human merger is misled about the verdict; the comment history becomes ambiguous. The merge gate itself is unaffected because branch protection reads the check run, and the updater filters on
- **Impacted Assets**: A022
- **Tags**: comment-spoofing, STRIDE-S
- **Residual Risk Decision**: Accepted
- **Residual Severity**: Low
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: The merge decision comes from the check run, not from comments, and the updater filters on the bot author plus marker. A look-alike comment can only mislead a human reader; adding run id/SHA to the marker and documenting the check run as authoritative (M057) is cheap hygiene.
- **Assessment State**: Current

#### T18: Malicious or disgruntled contributor (TA013, TA008)

**Statement**: A Malicious or disgruntled contributor (TA013, TA008) Repository write access lets a user edit or delete any issue/PR comment, including the bot's; run logs expire after the retention period; execution_file is not uploaded as an artifact. can Edits the posted review comment after the fact (e.g., removes the BLOCK verdict text) or waits out log retention so the model's reasoning for a pass/block cannot be reconstructed., which leads to Loss of an auditable record of what the reviewer actually said for a given SHA; disputes about why a change was allowed cannot be settled from the PR alone.

- **Prerequisites**: Repository write access lets a user edit or delete any issue/PR comment, including the bot's; run logs expire after the retention period; execution_file is not uploaded as an artifact.
- **Action**: Edits the posted review comment after the fact (e.g., removes the BLOCK verdict text) or waits out log retention so the model's reasoning for a pass/block cannot be reconstructed.
- **Impact**: Loss of an auditable record of what the reviewer actually said for a given SHA; disputes about why a change was allowed cannot be settled from the PR alone.
- **Impacted Assets**: A022, A024
- **Tags**: audit-trail, STRIDE-R
- **Residual Risk Decision**: Accepted
- **Residual Severity**: Low
- **Residual Likelihood**: Possible
- **Residual Risk Rationale**: Check-run annotations and run logs preserve the verdict for the log retention period; the comment is editable by design of GitHub. For a demo repository this is acceptable; upload artifacts (M055) if the pattern is reused where audit evidence matters.
- **Assessment State**: Current

#### T20: External fork author (TA002, TA007) enabled by maintainer mistake (TA009)

**Statement**: A External fork author (TA002, TA007) enabled by maintainer mistake (TA009) A maintainer adds the fork lane the README recommends but implements it with pull_request_target (or workflow_run) and checks out the fork head, or passes fork content to an agent with secrets can Opens a fork PR whose content is executed or reviewed in a privileged default-branch context with repository secrets and a write-capable token ('pwn request')., which leads to Anonymous internet users gain everything TA013 has: credential exfiltration, gate bypass, comment forgery. Not present today because every step is skipped for forks and secrets are withheld.

- **Prerequisites**: A maintainer adds the fork lane the README recommends but implements it with pull_request_target (or workflow_run) and checks out the fork head, or passes fork content to an agent with secrets
- **Action**: Opens a fork PR whose content is executed or reviewed in a privileged default-branch context with repository secrets and a write-capable token ('pwn request').
- **Impact**: Anonymous internet users gain everything TA013 has: credential exfiltration, gate bypass, comment forgery. Not present today because every step is skipped for forks and secrets are withheld.
- **Impacted Assets**: A016, A017, A018, A019
- **Tags**: pull_request_target, fork, future-change, STRIDE-E
- **Residual Risk Decision**: Mitigated
- **Residual Severity**: Low
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: Only the pull_request trigger is used, every step carries the fork guard, the job name differs on forks and GitHub withholds secrets from fork runs. This is a design constraint to preserve: any future fork lane must follow M047, never pull_request_target with a head checkout.
- **Assessment State**: Current

#### T23: Asset service client (persona) / external attacker (TA002)

**Statement**: A Asset service client (persona) / external attacker (TA002) A deployment of the demo app; a merged change that replaces the resolved-path containment with a lexical check or removes it (the outcome T002/T001/T003 aim for). can Requests img/../../secret.txt or a path through a symlink inside the asset tree that points outside it., which leads to Arbitrary file read from the asset host; the vulnerability the whole gate exists to keep out of main. Currently prevented by resolve_asset's Path.resolve() containment (root == candidate or root in

- **Prerequisites**: A deployment of the demo app; a merged change that replaces the resolved-path containment with a lexical check or removes it (the outcome T002/T001/T003 aim for).
- **Action**: Requests img/../../secret.txt or a path through a symlink inside the asset tree that points outside it.
- **Impact**: Arbitrary file read from the asset host; the vulnerability the whole gate exists to keep out of main. Currently prevented by resolve_asset's Path.resolve() containment (root == candidate or root in
- **Impacted Assets**: A025
- **Tags**: path-traversal, protected-target, STRIDE-I
- **Residual Risk Decision**: Mitigated
- **Residual Severity**: Low
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: resolve_asset rejects empty, padded and absolute paths and requires the fully resolved candidate to be the root or under it, which defeats img/../../secret.txt and symlink escapes. The no-guard-removal rule exists to keep this true; residual risk is T002 (a false negative on a future weakening).
- **Assessment State**: Current

#### T24: Asset service client (persona) / anyone with log access

**Statement**: A Asset service client (persona) / anyone with log access A deployment of the demo app; a merged change that logs the raw presented token, bypasses describe_token, or replaces hmac.compare_digest with == (timing side channel). can Harvests full API tokens from warning logs or recovers them byte-by-byte via response timing., which leads to Credential exposure for the demo service. Currently prevented by describe_token (4-char prefix + length) and constant-time comparison; the semgrep logger-credential-disclosure hit on tokens.py:29 is

- **Prerequisites**: A deployment of the demo app; a merged change that logs the raw presented token, bypasses describe_token, or replaces hmac.compare_digest with == (timing side channel).
- **Action**: Harvests full API tokens from warning logs or recovers them byte-by-byte via response timing.
- **Impact**: Credential exposure for the demo service. Currently prevented by describe_token (4-char prefix + length) and constant-time comparison; the semgrep logger-credential-disclosure hit on tokens.py:29 is
- **Impacted Assets**: A025
- **Tags**: secret-logging, timing, protected-target, STRIDE-I
- **Residual Risk Decision**: Mitigated
- **Residual Severity**: Low
- **Residual Likelihood**: Unlikely
- **Residual Risk Rationale**: hmac.compare_digest removes the timing channel and describe_token limits logs to a 4-character prefix plus length; the semgrep hit on the format string is a false positive by design. The no-secret-logging rule guards against regression.
- **Assessment State**: Current

### Not Useful Threats

#### T21: Third-party model provider (TA010); anyone with access to invocation logs

**Statement**: A Third-party model provider (TA010); anyone with access to invocation logs The pattern is copied to a private or proprietary repository; the Anthropic API fallback is used (different retention terms than Bedrock); or Bedrock model invocation logging is enabled without can Source code, the diff and any file the agent reads leave the repository boundary inside prompts., which leads to For this public repository: none. For reuse on private code: disclosure of source to the provider or to over-broad log readers. Bedrock does not store prompts or share them with model providers

- **Prerequisites**: The pattern is copied to a private or proprietary repository; the Anthropic API fallback is used (different retention terms than Bedrock); or Bedrock model invocation logging is enabled without
- **Action**: Source code, the diff and any file the agent reads leave the repository boundary inside prompts.
- **Impact**: For this public repository: none. For reuse on private code: disclosure of source to the provider or to over-broad log readers. Bedrock does not store prompts or share them with model providers
- **Impacted Assets**: A014
- **Tags**: data-handling, reuse, STRIDE-I, aws-docs-validated
- **Residual Risk Decision**: Not Applicable
- **Residual Risk Rationale**: The repository is public and Apache-2.0; the diff and source carry no confidentiality requirement, and the primary Bedrock path does not store or share prompts per AWS documentation. Becomes relevant only if the pattern is reused on non-public code (M059).
- **Assessment State**: Current

## Mitigations

### Resolved Mitigations

#### M1: IMPLEMENTED: Review contract (RULES.yaml, discovery.md, validate.md) is loaded from the pull request BASE commit, never from the PR head; a missing or empty prompt fails the job.

**Addresses Threats**: T1, T4

#### M2: IMPLEMENTED: Code-only agent tool allow-list (Read, Grep, Glob) with a 40-turn cap in both passes; the agent has no execution or network tool.

**Addresses Threats**: T1, T6, T8, T19

#### M3: IMPLEMENTED: The diff is prefetched as a data file outside the checkout and the invocation prompt contains no PR title, body or comments; the agent never runs git or gh.

**Addresses Threats**: T1, T16

#### M4: IMPLEMENTED: Two independent model invocations (discovery then falsification) with prompts that treat in-diff text and the candidate list as untrusted, require code-grounded evidence, and limit BLOCKING to a closed list.

**Addresses Threats**: T1, T2, T14, T15

#### M5: IMPLEMENTED: Deterministic fail-closed gate on SHA-scoped markers; every abnormal path (errored step, empty output, missing marker, oversized candidates) exits 1, and a CI step, not the model, posts the single PR comment.

**Addresses Threats**: T1, T13, T17, T19

#### M6: IMPLEMENTED: Credential hygiene: checkout token not persisted, minimal job permissions, cloud credentials assumed last and only when Bedrock is configured.

**Addresses Threats**: T6, T7

#### M8: IMPLEMENTED: Fork guard on every step plus a distinct job name for fork PRs, relying on GitHub withholding secrets from fork-triggered pull_request events.

**Addresses Threats**: T20

#### M9: IMPLEMENTED: All third-party actions pinned to full commit SHAs with version comments; Python test dependencies version-pinned.

**Addresses Threats**: T7

#### M10: IMPLEMENTED: Scratch paths are removed before being recreated and the diff lives under $RUNNER_TEMP, so PR-committed files or symlinks at those paths cannot redirect writes or pre-seed gate inputs.

**Addresses Threats**: T16

#### M11: IMPLEMENTED: Blocking rule 'rules-may-only-tighten' makes any weakening of RULES.yaml, the prompts or the workflow a BLOCKING finding when reviewed against the base contract.

**Addresses Threats**: T3, T4

#### M12: IMPLEMENTED (partial): Per-PR concurrency cancellation, 30-minute job timeout, 40-turn cap per pass and a candidate-size cap bound the cost of a single PR's review.

**Addresses Threats**: T12, T15

#### M13: IMPLEMENTED: Demo app guards: resolved-path containment (follows symlinks), absolute/empty path rejection, constant-time token comparison and prefix-only token logging.

**Addresses Threats**: T23, T24

#### M14: IMPLEMENTED: Blocking rules no-guard-removal and no-secret-logging give the reviewer an explicit checklist for the two app guards, including the specific weak replacements attackers use.

**Addresses Threats**: T2, T23, T24

#### M15: IMPLEMENTED: The unit-test job that executes PR code runs with a read-only token, no repository secrets and a non-persisted checkout credential.

**Addresses Threats**: T9

### In Progress Mitigations

#### M7: IMPLEMENTED (partial): Regex redaction of AWS key ids, ARNs, 12-digit account ids and labelled secret values in model output before it is logged or posted, on top of GitHub's exact-string secret masking.

**Addresses Threats**: T6

#### M29: When reusing the pattern on non-public code, keep model calls on Bedrock with restricted invocation logging (or zero retention) and review the Anthropic API fallback's data terms.

**Addresses Threats**: T21

#### M30: Define the recovery path for outages and false blocks: bounded retries, documented re-run, and a code-owner override procedure that never weakens the required check.

**Addresses Threats**: T13, T14

### Identified Mitigations

#### M16: Protect .github/** and RULES.yaml with CODEOWNERS plus a branch ruleset that requires code-owner review and forbids bypass, so a PR cannot merge a modified reviewer without a second human.

**Addresses Threats**: T3, T4, T5, T8, T20

#### M17: Move the privileged review job to a default-branch-defined workflow_run lane that consumes the PR diff as an artifact, so the code that reviews a PR can never be edited by that PR (and fork PRs can be reviewed safely).

**Addresses Threats**: T3, T20

#### M18: Verify branch protection/rulesets on main: required checks match the current job names exactly, no admin bypass, PR required; pin the check name in the workflow-invariants test.

**Addresses Threats**: T3, T5

#### M19: Harden the Bedrock IAM role: repository-scoped OIDC subject and audience conditions, InvokeModel-only permissions on the exact inference-profile/foundation-model ARNs, and the shortest practical session duration.

**Addresses Threats**: T6, T10, T11

#### M20: Add cost and misuse monitoring: Bedrock budget and invocation alarms, model invocation logging with restricted access, CloudTrail alerting on role assumption, GitHub Actions spending limit, and trigger filters that skip draft or docs-only PRs.

**Addresses Threats**: T6, T7, T10, T11, T12

#### M21: Constrain what the agent's Read tool can reach: deny-list /proc, home, temp and .git paths via Claude Code permission settings, drop the unused ANTHROPIC_API_KEY input when Bedrock is active, and consider a container job with a minimal filesystem.

**Addresses Threats**: T1, T6, T8

#### M22: Treat secret-shaped content in model output as a gate failure rather than something to redact: broaden the patterns (raw AWS secret keys, GitHub and Anthropic token prefixes, JWTs, long base64 blobs) and withhold the output entirely when they match.

**Addresses Threats**: T6

#### M23: Add an upper bound on reviewable diff size and reject Trojan-Source characters, so an attacker cannot exhaust the agents' turns or context to hide a small change.

**Addresses Threats**: T12, T15

#### M24: Close the run-time install gap: pin the Claude Code CLI version, hash-pin Python test dependencies, and review action updates through Dependabot before adopting new SHAs.

**Addresses Threats**: T7, T9, T19

#### M25: Preserve an audit trail independent of editable PR comments: upload the redacted outputs and execution transcript as workflow artifacts and reference run id and SHA in the comment.

**Addresses Threats**: T18

#### M26: Measure the reviewer empirically against the attack corpus after every model, prompt or action change, and pin model ids so behaviour changes are deliberate.

**Addresses Threats**: T1, T2, T13, T14

#### M27: Make the bot comment unambiguous and non-authoritative: include run id and SHA in the marker, keep lane markers distinct, and document that the check run, not the comment, is the verdict.

**Addresses Threats**: T17, T18

#### M28: Scope the secret-derived USE_BEDROCK expression to the job (or a single step) instead of the workflow-level env block (ASH finding 1).

**Addresses Threats**: T22

## Assumptions

### A001: Business scope

**Description**: The repository is public and Apache-2.0 licensed; the source code and the PR diffs have no confidentiality requirement. Confidentiality concerns are limited to the workflow credentials.

- **Impact**: Threats about code disclosure to the model provider or in logs are out of scope; threats about credential disclosure remain in scope.
- **Rationale**: README describes a conference demo published as a sample; LICENSE is Apache-2.0; every attack scenario is documented publicly.

### A002: Business scope

**Description**: The system under analysis is the AI review gate (agentic-review.yml, review prompts, RULES.yaml, ci.yml). The Python app under app/ is the demo review target and is not deployed as a service anywhere.

- **Impact**: App threats are modelled only as the thing the gate must protect (guard removal, secret logging), not as a running production endpoint.
- **Rationale**: app/__init__.py states 'Nothing here is production code'; there is no HTTP layer, packaging, or deployment configuration in the checkout.

### A003: Business scope

**Description**: Files referenced by the README but absent from this checkout (naive-review.yml, demo/, tests/, talk/) are out of scope. In particular the deliberately insecure naive lane is not analysed.

- **Impact**: The threat model covers the hardened lane only; if the naive lane is added to the same repository, its weaknesses (Bash tool, PR body in prompt, HEAD rules) would create additional exposure for the same secrets.
- **Rationale**: Only the files present in the working tree can be validated in Phase 7.5.

### A004: Deployment

**Description**: The workflow runs on GitHub-hosted ubuntu-latest runners and calls Amazon Bedrock in vars.AWS_REGION (default us-west-2) through an IAM role assumed via GitHub OIDC. The Anthropic API path is a fallback the maintainer may configure instead.

- **Impact**: Data residency is US; the security of the runner OS and network is GitHub's responsibility; the IAM role trust policy is the maintainer's responsibility.
- **Rationale**: runs-on: ubuntu-latest; aws-actions/configure-aws-credentials with role-to-assume; README setup step 2.

### A005: Deployment

**Description**: Branch protection (or a ruleset) on main requires the 'Agentic AI Review' and 'Unit tests' status checks, requires a PR, and has admin bypass disabled. Without this, the gate is advisory.

- **Impact**: If this assumption fails, every gate-bypass threat becomes trivially exploitable by anyone with write access (T005). Tracked as mitigation M048.
- **Rationale**: Earlier README revisions instructed this in setup step 4; the current README no longer documents it at all, and repository settings cannot be verified from the checkout. The lane was renamed from 'Hardened AI Review' to 'Agentic AI Review' during this session, so any existing rule naming the old check no longer applies.

### A006: Deployment

**Description**: The IAM role for AWS_BEDROCK_ROLE_ARN trusts only this repository's OIDC subject (repo:<owner>/<repo>:pull_request or narrower) and grants only bedrock:InvokeModel* on the inference profiles used.

- **Impact**: A broader trust policy (e.g., sub wildcard) would let other repositories assume the role; broader permissions would raise the impact of credential exposure.
- **Rationale**: README setup step 2 describes this configuration; not verifiable from the repository.

### A007: Threat model

**Description**: The primary adversary is a same-repository contributor with write access (or an attacker holding such an account), because only same-repo PRs run the workflow with secrets.

- **Impact**: Insider and compromised-account threats are prioritised over anonymous external attackers, who are stopped at the fork guard.
- **Rationale**: Every step is guarded by head.repo.full_name == github.repository, and GitHub does not pass secrets to fork-triggered pull_request runs.

### A008: Financial

**Description**: The financial impact of a compromise is bounded by model invocation cost within the Bedrock role's permissions plus reputational damage to a security sample; no customer data or revenue-bearing system is involved.

- **Impact**: Financial impact tier Low; availability tier 99%.
- **Rationale**: Bedrock role is scoped to InvokeModel; there is no data store or customer-facing service.

### A009: Architecture

**Description**: The IAM role trust policy for AWS_BEDROCK_ROLE_ARN sets both token.actions.githubusercontent.com:aud = sts.amazonaws.com and a token.actions.githubusercontent.com:sub condition scoped to this repository (e.g. repo:<owner>/<repo>:pull_request), per AWS guidance that an unscoped sub lets any GitHub organization or repository assume the role. Reference: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html

- **Impact**: If false, the Bedrock role is assumable from arbitrary GitHub repositories and the credential-exposure threats gain an external, unauthenticated attacker path.
- **Rationale**: AWS IAM documentation (Configuring a role for GitHub OIDC identity provider) states the sub condition must be present and must limit access to specific organizations/repositories; the repository itself cannot enforce this.

### A010: Architecture

**Description**: The role's permission policy grants only bedrock:InvokeModel and bedrock:InvokeModelWithResponseStream on the specific inference-profile and foundation-model ARNs used (default profiles us.anthropic.claude-sonnet-4-6 and us.anthropic.claude-opus-4-8), following AWS's least-privilege examples for Bedrock model access. Reference: https://aws.amazon.com/blogs/security/simplified-amazon-bedrock-model-access/

- **Impact**: Bounds the blast radius of leaked STS credentials to model invocation cost on approved models for the remaining session lifetime (default 1 hour).
- **Rationale**: README setup step 2 instructs bedrock:InvokeModel* on the inference profiles used; AWS guidance shows scoping Resource to inference-profile and foundation-model ARNs rather than *.

### A011: Architecture

**Description**: anthropics/claude-code-action, in prompt-driven mode with --allowedTools Read,Grep,Glob, does not expose any tool that performs network egress or GitHub API writes to the model, and does not inject PR title/body into the model context. The github_token input is used only by the action's own plumbing.

- **Impact**: If false, prompt injection could reach the agent through PR metadata or the agent could exfiltrate data directly, bypassing the CI-mediated output channel. Modelled as a threat with a residual risk rather than assumed away.
- **Rationale**: The workflow comment and README assert 'No PR title, body, or comments ever enter its context. No Bash, no network.' This depends on the third-party action's implementation at the pinned SHA and cannot be verified from this repository.

### A012: Threat actors

**Description**: Nation-state, competitor, terrorist and cyber-mercenary actors are not relevant: the repository is a public demo with no proprietary data, no customers and no infrastructure beyond a model-invocation role.

- **Impact**: Threat identification focuses on Tier 1-3 actors; advanced persistent techniques (runner escape, GitHub platform compromise) are out of scope.
- **Rationale**: Business context: Public code, Low criticality, Low financial impact, no regulated data.

### A013: Threat actors

**Description**: Anyone able to open a same-repository pull request is treated as fully adversarial, regardless of employment relationship, because GitHub account compromise is common and the workflow cannot distinguish a compromised account from a malicious one.

- **Impact**: Every control is evaluated against an attacker who can change any file in the PR head, including the workflow file itself.
- **Rationale**: The gate's design premise (README) is that the reviewer reads attacker-controlled input; the four attack PRs are authored from a write-access account.

### A026: Asset protection

**Description**: GitHub masks registered secret values and the AWS credentials exported by configure-aws-credentials in step logs, but masking is exact-string based: values that are transformed (base64, split, reversed) or quoted by the model in a different form are not masked. The workflow's own perl redaction is therefore treated as the effective control for model output.

- **Impact**: Threats about credential disclosure via model output must consider redaction-bypass encodings; a raw AWS secret access key without its label is not matched by either mechanism.
- **Rationale**: GitHub Actions log masking documentation; the workflow adds explicit redaction of key-id, ARN, account-id and labelled-secret shapes before cat/post.

### A027: Asset protection

**Description**: AWS STS session credentials issued to the role remain valid until their expiry (default 1 hour) even after the GitHub job finishes; the repository does not use a shorter role-duration-seconds.

- **Impact**: A leaked session gives an attacker up to an hour of Bedrock invocation on the maintainer's account.
- **Rationale**: configure-aws-credentials step sets no role-duration-seconds; AWS default session duration is 1 hour.

### A028: Threats

**Description**: SHA-scoped markers cannot be pre-planted in PR content: the head SHA depends on the content, so an author cannot commit a file containing '[REVIEWED] <head sha>' for that same commit. Marker forgery therefore requires steering the model (T001) or changing the workflow (T003), and replaying an earlier run's output is impossible.

- **Impact**: Direct marker injection through the diff is excluded from the threat list; nondeterministic model behaviour and workflow tampering remain the bypass routes.
- **Rationale**: Git object hashing; the gate greps review-output.md (model output) for the marker plus the exact head SHA supplied at run time.

### A029: Threats

**Description**: Claude Code's --allowedTools 'Read,Grep,Glob' in non-interactive mode denies every other tool (Bash, Write, Edit, WebFetch, MCP tools) rather than merely skipping approval prompts; the README reports the denial as visible in transcripts.

- **Impact**: Code-execution threats (T008) are rated Unlikely as long as the allow-list is unchanged; T003 (workflow edit) is the path to changing it.
- **Rationale**: Design basis of CONTROL 2; the four attack PRs were measured against it per the README.

### A030: Mitigations

**Description**: The maintainer will apply the GitHub-side mitigations (CODEOWNERS on .github/** and RULES.yaml, rulesets without bypass, required check names) before relying on the gate for anything beyond the demo; these cannot be expressed in the repository's files and are therefore tracked as identified, not resolved.

- **Impact**: Until applied, T003 (workflow edit) and T005 (misconfigured protection) remain the dominant open risks.
- **Rationale**: Branch protection, rulesets and CODEOWNERS enforcement are repository settings; CODEOWNERS could be committed but is absent from this checkout.

### A031: Mitigations

**Description**: anthropics/claude-code-action at the pinned SHA accepts a Claude Code settings/permissions input (or honours a checked-in .claude/settings.json) that can deny Read on specific paths; if it does not, the equivalent constraint requires running the agent in a container job with a minimal filesystem.

- **Impact**: M051's feasibility and cost depend on this; if unavailable, M052 (withhold secret-shaped output) and M049 (short sessions) carry more weight for T006.
- **Rationale**: Claude Code supports permissions.deny rules for tools with path patterns; the action's exact inputs at v1.0.217 were not verified in this session.

### A032: Residual risk

**Description**: Risk acceptance criteria used in Phase 8: a threat is Accepted only where the README explicitly names the trade-off (cost of two model calls, nondeterministic verdicts, fail-closed outages) or where the impact is bounded to public code or human confusion without affecting the check run. Everything that could turn the gate green on attacker terms, or expose credentials, stays Open until the owner acts.

- **Impact**: Six threats Accepted, seven Mitigated, one Not Applicable, ten Open. The Open set is dominated by items outside the code (branch protection, IAM policies) and by the workflow-edit gap.
- **Rationale**: The system's only purpose is to be a trustworthy merge gate; the business context rates the repository Low criticality but the gate's integrity is its entire value.

### A033: Residual risk

**Description**: The residual-risk decisions recorded here are the analyst's proposals; the repository owner has not yet reviewed or approved them.

- **Impact**: Decisions marked Accepted should be confirmed (or reopened) by the maintainer before the model is treated as the record of accepted risk.
- **Rationale**: Acceptance of risk is an owner decision; this session produced the model without an owner review step.

## Phase Progress

| Phase | Name | Completion |
|---|---|---|
| 1 | Business Context Analysis | 100% ✅ |
| 2 | Architecture Analysis | 100% ✅ |
| 3 | Threat Actor Analysis | 100% ✅ |
| 4 | Trust Boundary Analysis | 100% ✅ |
| 5 | Asset Flow Analysis | 100% ✅ |
| 6 | Threat Identification | 100% ✅ |
| 7 | Mitigation Planning | 100% ✅ |
| 7.5 | Code Validation Analysis | 100% ✅ |
| 8 | Residual Risk Analysis | 100% ✅ |
| 9 | Output Generation and Documentation | 100% ✅ |

---

*This threat model report was generated automatically by the Threat Modeling MCP Server.*
