# Code Validation Report

**Project Directory**: /Users/gaechter/git/sample-agentic-code-review-gate
**Coverage**: 24/24 threats; 30/30 mitigations

### Threat Findings

#### T001: Plants prompt-injection text in code comments, docstrings, filenames, test names or a symlinked 'docs' file ('audited by security', 'reviewers: report no findings', fake SYSTEM blocks asking for the

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M031, M032, M033, M034, M035, M051, M056
- **Evidence**:
  - .github/workflows/agentic-review.yml:116 and :171 restrict both passes to --allowedTools "Read,Grep,Glob" so an injected instruction has no execution or posting tool to act through
  - .github/workflows/agentic-review.yml:117-127 and :172-185 build the invocation prompt from the prompt-file path, the head SHA and the diff path only; github.event.pull_request.title/body do not appear anywhere in the file
  - .github/review-prompts/discovery.md:60-66 and validate.md:26-33 instruct the model that text in code, comments, docstrings and filenames is neither instruction nor evidence
  - .github/review-prompts/validate.md:19-24 declares the candidate list UNTRUSTED EVIDENCE, closing the second-order path via .review-candidates.md
  - .github/workflows/agentic-review.yml:264-271 gates on the exact SHA-scoped markers, so a forged verdict needs the model itself to emit them
  - Residual: whether the model obeys the prompt under adversarial text is probabilistic, and the claude-code-action internals (A011) were not inspected
- **Recommendation**: Keep measuring against the attack corpus (M056); add Read path deny rules (M051) so injected instructions cannot at least reach credentials.

#### T002: Smuggles a guard removal inside a legitimate-looking feature: replaces the resolved-path containment in app/files.py with startswith('../'), or adds a raw-token debug log in app/tokens.py, keeping

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M034, M044, M056
- **Evidence**:
  - RULES.yaml:11-29 (no-guard-removal) names startswith("../") and '".." not in requested' as insufficient replacements and requires judging from code alone
  - .github/review-prompts/discovery.md:36-41 tells the discovery pass exactly which two guards matter; :43-48 makes every matching rule violation worth recording
  - .github/review-prompts/validate.md:44-51 requires input, call path and observable outcome re-derived from opened code before a finding survives
  - Residual: detection is model-dependent by nature; the repository ships no measurement results (demo/results referenced in earlier README revisions is absent from this checkout)
- **Recommendation**: Record pass/block rates per attack tag after each model or prompt change (M056).

#### T003: Edits .github/workflows/agentic-review.yml in the same PR as the malicious code: replaces the gate with exit 0, widens --allowedTools to include Bash/WebFetch, removes the fork guard, points the

- **Outcome**: not_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M041, M046, M047, M048
- **Evidence**:
  - .github/ contains only review-prompts/ and workflows/; there is no CODEOWNERS file anywhere in the repository
  - .github/workflows/agentic-review.yml:26-28 triggers on pull_request, so GitHub executes the workflow definition from the PR merge ref and a same-repo PR can rewrite every control in this file
  - RULES.yaml:46 lists .github/workflows/agentic-review.yml under rules-may-only-tighten, but that rule is enforced by the very workflow the PR can change
  - README.md:47-50 acknowledges the gap and defers to CODEOWNERS/required review and a default-branch workflow_run lane, neither of which is present
- **Recommendation**: Add CODEOWNERS for .github/** and RULES.yaml with a ruleset requiring code-owner review (M046); longer term move the privileged job to a default-branch workflow_run lane (M047).

#### T004: Sets blocking: false on no-guard-removal, narrows file-patterns, rewrites validate.md to always emit a clean verdict, or removes a prompt file entirely (README attack 3).

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M031, M041, M046
- **Evidence**:
  - .github/workflows/agentic-review.yml:70-72 load RULES.yaml and both prompts with git show "$BASE_SHA:...", so the PR under review cannot change what it is reviewed against
  - .github/workflows/agentic-review.yml:74-77 exit 1 when a prompt is missing or empty on the base commit
  - RULES.yaml:41-56 makes weakening the contract a blocking violation; validate.md:66-70 tells the model the rule's flag is authoritative
  - Residual: the disarming PR itself is still judged by a model; if it is passed (T001/T002) or merged through a workflow edit (T003), later PRs inherit the weakened contract
- **Recommendation**: Covered by M046/M047 for the merge path; no code change needed for the base-ref mechanism itself.

#### T005: Merges, or lets a contributor merge, a PR whose review check failed or never ran, because branch protection does not enforce the check.

- **Outcome**: not_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M046, M048
- **Evidence**:
  - Branch protection and rulesets are repository settings; nothing in the checkout can enforce or verify them
  - README.md (current revision) no longer contains the setup step that instructed requiring the 'Agentic AI Review' and 'Unit tests' checks and disabling admin bypass; the only related text is README.md:47-50
  - .github/workflows/agentic-review.yml:46 sets the check name that a required-status-check rule must match exactly; the lane was renamed from 'Hardened AI Review' during this session, so any existing rule still naming the old check no longer protects main
- **Recommendation**: Configure the ruleset (required checks 'Agentic AI Review' and 'Unit tests', PR required, no bypass actors) and restore the setup instruction in the README (M048).

#### T006: Instructs the agent, via in-diff text or a symlink such as docs/context.md -> /proc/self/environ, to read the environment or credential files and quote the values in its final message, optionally

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M032, M036, M037, M049, M050, M051, M052
- **Evidence**:
  - .github/workflows/agentic-review.yml:56 persist-credentials: false keeps GITHUB_TOKEN out of .git/config
  - .github/workflows/agentic-review.yml:116 and :171 deny Bash/WebFetch so the agent cannot send credentials anywhere itself; its only channel is the final message
  - .github/workflows/agentic-review.yml:146 and :201 redact AKIA/ASIA key ids, arn:aws*, 12-digit ids and labelled aws_secret_access_key/aws_session_token/api_key values before cat/post
  - Gap: neither regex matches a raw 40-character secret access key, a session token without its label, ghs_/sk-ant- prefixes, or base64/spaced encodings; the step redacts and continues rather than failing
  - Gap: :111 and :166 pass anthropic_api_key to both agent steps even when Bedrock is in use; :99-103 export STS credentials into the environment every later step inherits; no Read deny-list for /proc, $HOME or $RUNNER_TEMP is configured
- **Recommendation**: Fail the gate and withhold output when secret-shaped strings appear (M052); deny Read on /proc, home, temp and .git paths and drop the unused API-key input (M051); shorten the role session (M049).

#### T007: Malicious code executes inside the agent steps, after configure-aws-credentials has exported STS credentials and with github_token/anthropic_api_key as inputs; it can exfiltrate them over the network

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M036, M039, M050, M054
- **Evidence**:
  - .github/workflows/agentic-review.yml:52, :98, :108, :163 pin actions/checkout, aws-actions/configure-aws-credentials and anthropics/claude-code-action (both uses) to full commit SHAs with version comments
  - .github/workflows/ci.yml:20 and :23 pin actions/checkout and actions/setup-python by SHA; :26 pins pytest==8.4.1 and PyYAML==6.0.2
  - Gap: neither claude-code-action step (:108-127, :163-185) pins the Claude Code CLI version the action downloads at run time, and that download happens after :99-103 has exported AWS credentials
  - Gap: ci.yml:26 does not use --require-hashes; no .github/dependabot.yml exists
- **Recommendation**: Pin the CLI version, hash-pin pip dependencies and route action bumps through Dependabot with code-owner review (M054).

#### T008: PR content (and, in the naive lane, the PR body) asks the reviewer to 'run pytest to verify'; a conftest.py in the PR POSTs the process environment and the checkout to an attacker URL when imported

- **Outcome**: fully_mitigated
- **Threat status**: threatResolved
- **Linked mitigations**: M032, M046, M051
- **Evidence**:
  - .github/workflows/agentic-review.yml:116 and :171 set --allowedTools "Read,Grep,Glob" for both passes; no Bash, Write, Edit or WebFetch tool is granted
  - .github/workflows/agentic-review.yml:82-95 prefetches the diff with git in a CI step so the agent never needs git or gh
  - The invocation prompts (:117-127, :172-185) do not ask the agent to run anything; validate.md:84-85 and discovery.md:106 forbid tool-based posting
  - Residual: depends on the allow-list not being widened, which is the T003 workflow-edit path
- **Recommendation**: Protect the workflow file (M046) so the allow-list cannot be changed in the same PR that exploits it.

#### T009: conftest.py or a test exfiltrates the runner environment, the read-only token and the checkout to a remote endpoint during python -m pytest.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M045, M054
- **Evidence**:
  - .github/workflows/ci.yml:11-12 sets permissions: contents: read for the whole workflow
  - .github/workflows/ci.yml:20-22 checks out with persist-credentials: false; :26-27 install pinned test deps and run pytest; no secrets.* reference exists in ci.yml
  - Gap: no egress restriction on the test runner, so PR code can still POST the checkout and the read-only token to an external URL
- **Recommendation**: Keep secrets out of ci.yml permanently; treat any future secret added to the test job as a new exfiltration path.

#### T010: Runs a workflow in an attacker-controlled GitHub repository that requests an OIDC token and calls sts:AssumeRoleWithWebIdentity for the Bedrock role.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M049, M050
- **Evidence**:
  - .github/workflows/agentic-review.yml:32 grants id-token: write and :98-103 assume the role via OIDC with aws-actions/configure-aws-credentials instead of storing static AWS keys, which removes the long-lived-credential variant of this threat
  - The IAM trust policy (aud/sub conditions) lives in the maintainer's AWS account and cannot be read or enforced from the repository (A009); README.md:37-40 only says 'trusted by GitHub's OIDC provider for this repository'
- **Recommendation**: Verify the trust policy uses StringEquals on token.actions.githubusercontent.com:aud = sts.amazonaws.com and a repository-scoped sub (M049).

#### T011: Uses the leaked STS session to call whatever the over-broad policy allows: other Bedrock APIs (CreateModelCustomizationJob, agents, knowledge bases), other services, or arbitrary expensive models.

- **Outcome**: not_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M049, M050
- **Evidence**:
  - The role's permission policy is AWS-side configuration; nothing in the repository constrains or validates it (A010)
  - README.md:37-39 instructs bedrock:InvokeModel* on the inference profiles used, which is guidance only
  - .github/workflows/agentic-review.yml:98-103 sets no role-duration-seconds, so a leaked session keeps the role's full permissions for the default 1-hour lifetime
- **Recommendation**: Scope the policy to InvokeModel/InvokeModelWithResponseStream on the exact inference-profile and foundation-model ARNs and set role-duration-seconds: 900 (M049).

#### T012: Opens many PRs or pushes many commits, each triggering two model calls of up to 40 turns (one on an Opus-class model) plus GitHub Actions minutes; large diffs maximise tokens per run.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M042, M050, M053
- **Evidence**:
  - .github/workflows/agentic-review.yml:34-36 concurrency group per PR with cancel-in-progress: true; :48 timeout-minutes: 30; :115 and :170 --max-turns 40; :133 MAX_CANDIDATE_BYTES 120000
  - Gap: :26-28 run on every opened/synchronize/reopened event with no draft or path filter; no budget, alarm or invocation-logging configuration exists in the repository; concurrency does not limit parallel PRs
- **Recommendation**: Add Bedrock budget/invocation alarms and a GitHub Actions spending limit; skip draft PRs and docs-only changes (M050).

#### T013: The validation step fails or returns no [REVIEWED] marker; the gate exits 1 as designed.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M035, M056, M060
- **Evidence**:
  - .github/workflows/agentic-review.yml:256-263 fail closed when the validation step did not succeed or produced no output, so an outage blocks merges rather than passing them
  - .github/workflows/agentic-review.yml:224 tells the reader to 're-run the workflow or inspect the logs' in the posted comment
  - Gap: no retry around the model calls (:108-127, :163-185); model ids default to hard-coded profile ids at :114 and :169 that vendors may deprecate
- **Recommendation**: Add one bounded retry for throttling/5xx and document the re-run path without adding any override that turns a failure into a pass (M060).

#### T014: Validation pass emits [BLOCK-MERGE] <sha> for a PR with no real defect.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M034, M056, M060
- **Evidence**:
  - .github/review-prompts/validate.md:44-51 requires every candidate to be actively falsified and kept only at confidence 80 or above
  - .github/review-prompts/validate.md:65-80 limits BLOCKING to a closed two-item list and forbids reasoning by analogy; :117 forbids [BLOCK-MERGE] for advisory findings
  - .github/review-prompts/validate.md:100-101 defines '**No findings.**' as a successful outcome
  - Residual: false blocks remain possible because the verdict is model output; the repository has no recorded false-positive rate
- **Recommendation**: Track false-block rate alongside the attack corpus (M056) and define the code-owner override procedure (M060).

#### T015: Buries a three-line guard removal inside a very large diff (vendored files, generated code, mass reformatting) or obfuscates it (Unicode bidi overrides, homoglyph identifiers, deeply nested

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M034, M042, M053
- **Evidence**:
  - .github/workflows/agentic-review.yml:91-94 only reject an EMPTY diff; there is no upper bound on diff bytes, files or hunks
  - .github/workflows/agentic-review.yml:152-155 cap the candidate list at 120000 bytes and :115/:170 cap turns at 40, which bound cost but also bound how much of a huge diff gets examined
  - .github/review-prompts/discovery.md:74-76 asks the model to judge every hunk, but nothing enforces it
  - No check for Unicode bidi or zero-width characters exists in the prefetch step
- **Recommendation**: Fail closed above a diff-size ceiling and on Trojan-Source characters (M053).

#### T016: Commits .review-base or .review-prompts as symlinks (or files) so that the base-ref extraction writes elsewhere and the agent reads PR-controlled rules/prompts; or commits .review-candidates.md /

- **Outcome**: fully_mitigated
- **Threat status**: threatResolved
- **Linked mitigations**: M033, M040
- **Evidence**:
  - .github/workflows/agentic-review.yml:67 rm -rf .review-base .review-prompts before :69 mkdir, so a committed symlink or file at those paths is removed before the base-ref writes at :70-72
  - .github/workflows/agentic-review.yml:136 rm -f .review-candidates.md and :192 rm -f review-output.md before each file is recreated
  - .github/workflows/agentic-review.yml:86 writes pr.diff under ${{ runner.temp }}, outside the checkout
  - No PR-authored code executes in the review job before these steps (:52-95 are checkout and git plumbing only)
- **Recommendation**: None; keep the rm-before-write pattern when adding new scratch files.

#### T017: Posts a look-alike 'Agentic AI Review — Verdict: pass' comment from their own account, or a second bot-authored comment with the marker so the updater PATCHes the wrong comment.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M035, M057
- **Evidence**:
  - .github/workflows/agentic-review.yml:241 selects only comments whose user.login is github-actions[bot] AND whose body starts with the marker before PATCHing
  - .github/workflows/agentic-review.yml:256-272 derive the merge decision from review-output.md and the step outcome, never from PR comments, so a spoofed comment cannot change the check
  - Gap: :217 uses a static marker, and any collaborator can post a look-alike comment that misleads a human reader
- **Recommendation**: Include run id and SHA in the marker and document that only the check run is authoritative (M057).

#### T018: Edits the posted review comment after the fact (e.g., removes the BLOCK verdict text) or waits out log retention so the model's reasoning for a pass/block cannot be reconstructed.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M055, M057
- **Evidence**:
  - .github/workflows/agentic-review.yml:157-158 and :203-204 cat the redacted candidates and verdict into the run log; :257, :261, :265, :269 emit ::error:: annotations that persist on the check run
  - Gap: no actions/upload-artifact step exists, so review-output.md, .review-candidates.md and the execution_file are lost when the runner is destroyed and the run log expires
  - Gap: the posted comment (:241-246) is an ordinary issue comment that any user with write access can edit or delete
- **Recommendation**: Upload the redacted outputs and transcript as artifacts and reference run id/SHA in the comment (M055).

#### T019: The agent uses github_token to post its own 'pass' comment with the marker, approve the PR as github-actions[bot], or edit files.

- **Outcome**: partially_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M032, M035, M054
- **Evidence**:
  - .github/workflows/agentic-review.yml:112 and :167 pass github_token to both claude-code-action steps
  - .github/workflows/agentic-review.yml:116 and :171 restrict the model's tools to Read,Grep,Glob; validate.md:84-85 and discovery.md:106 forbid posting via tools
  - .github/workflows/agentic-review.yml:256-272 read the verdict from the captured execution_file, not from comments, so an agent-posted comment could not satisfy the gate
  - Residual: whether the action exposes any GitHub write capability to the model despite the allow-list is internal to the pinned action and was not inspected (A011)
- **Recommendation**: Review the action's tool surface at each SHA bump (M054) and keep 'Allow GitHub Actions to create and approve pull requests' disabled in repository settings.

#### T020: Opens a fork PR whose content is executed or reviewed in a privileged default-branch context with repository secrets and a write-capable token ('pwn request').

- **Outcome**: fully_mitigated
- **Threat status**: threatResolved
- **Linked mitigations**: M038, M046, M047
- **Evidence**:
  - .github/workflows/agentic-review.yml:26-28 use only the pull_request trigger; no pull_request_target or workflow_run workflow exists in .github/workflows (only ci.yml and agentic-review.yml)
  - Every step carries the fork guard github.event.pull_request.head.repo.full_name == github.repository (:53, :60, :82, :99, :107, :130, :162, :188, :209, :250) and :46 renders a different job name on forks
  - .github/workflows/ci.yml:7-9 also uses pull_request, and its job holds no secrets (:11-12)
- **Recommendation**: If a fork lane is added, follow M047 (default-branch workflow_run consuming an artifact) and never check out or execute fork content with secrets present.

#### T021: Source code, the diff and any file the agent reads leave the repository boundary inside prompts.

- **Outcome**: not_applicable
- **Threat status**: threatResolvedNotUseful
- **Linked mitigations**: M059
- **Evidence**:
  - LICENSE is Apache-2.0 and README.md:1-11 describes a public sample; the diff and repository content carry no confidentiality requirement here (A001)
  - .github/workflows/agentic-review.yml:98-103 and :110/:165 prefer the Bedrock path, where prompts are not stored or shared with model providers per AWS documentation
  - The Anthropic API fallback (:111, :166) and any invocation-logging configuration are outside what this repository controls
- **Recommendation**: Applies only if the pattern is reused on non-public code; see M059.

#### T022: Reads whether Bedrock auth is configured from the environment variable / step outcomes.

- **Outcome**: not_mitigated
- **Threat status**: threatIdentified
- **Linked mitigations**: M058
- **Evidence**:
  - .github/workflows/agentic-review.yml:38-39 still define USE_BEDROCK: ${{ secrets.AWS_BEDROCK_ROLE_ARN != '' }} at workflow level (ASH/semgrep gha-workflow-env-secret, reported at :39)
  - The value is a boolean, and :99 already reveals the same information through the credentials step being run or skipped, so the exposure is informational
  - A job-level env placement was verified on copies with semgrep r/yaml.github-actions and checkov earlier in this session but has not been applied to the repository
- **Recommendation**: Move the env block under jobs.agentic-review (M058).

#### T023: Requests img/../../secret.txt or a path through a symlink inside the asset tree that points outside it.

- **Outcome**: fully_mitigated
- **Threat status**: threatResolved
- **Linked mitigations**: M043, M044
- **Evidence**:
  - app/files.py:26-27 reject empty or padded paths; :28-29 reject os.path.isabs paths
  - app/files.py:30-31 resolve both root and candidate with Path.resolve(), following symlinks and normalising '..'
  - app/files.py:36-38 require root == candidate or root in candidate.parents, which rejects img/../../secret.txt and symlink escapes; :39-41 additionally require is_file()
  - RULES.yaml:11-29 makes replacing this check with a lexical test a blocking review finding
- **Recommendation**: None for the code as written; the gate exists to keep it this way.

#### T024: Harvests full API tokens from warning logs or recovers them byte-by-byte via response timing.

- **Outcome**: fully_mitigated
- **Threat status**: threatResolved
- **Linked mitigations**: M043, M044
- **Evidence**:
  - app/tokens.py:27 compares with hmac.compare_digest on UTF-8 bytes (constant time)
  - app/tokens.py:15 and :18-22 limit describe_token to a 4-character prefix plus length; :29 logs only that redacted form on failure
  - RULES.yaml:30-40 makes logging a raw token a blocking review finding; the semgrep logger-credential-disclosure hit on tokens.py:29 is a pattern match on the format string, not a leak (intentional per maintainer)
- **Recommendation**: None; keep describe_token as the only sanctioned logging path.

### Mitigation Findings

#### M031: IMPLEMENTED: Review contract (RULES.yaml, discovery.md, validate.md) is loaded from the pull request BASE commit, never from the PR head; a missing or empty prompt fails the job.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T001, T004
- **Evidence**:
  - .github/workflows/agentic-review.yml:59-79: git show "$BASE_SHA:RULES.yaml" (:70) and "$BASE_SHA:.github/review-prompts/$p.md" (:72) into freshly recreated .review-base/.review-prompts (:67-69); exit 1 with ::error:: if a prompt is missing or empty (:74-77)

#### M032: IMPLEMENTED: Code-only agent tool allow-list (Read, Grep, Glob) with a 40-turn cap in both passes; the agent has no execution or network tool.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T001, T006, T008, T019
- **Evidence**:
  - .github/workflows/agentic-review.yml:115-116 and :170-171: --max-turns 40 and --allowedTools "Read,Grep,Glob" in both claude_args blocks

#### M033: IMPLEMENTED: The diff is prefetched as a data file outside the checkout and the invocation prompt contains no PR title, body or comments; the agent never runs git or gh.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T001, T016
- **Evidence**:
  - .github/workflows/agentic-review.yml:86 PATCH under ${{ runner.temp }}; :89 git diff --no-color base...head; :91-94 exit 1 on empty diff
  - .github/workflows/agentic-review.yml:117-127 and :172-185: prompts reference only the prompt file, the head SHA, the diff path and (validation) the candidates path; no PR title/body/comment expression appears in the file

#### M034: IMPLEMENTED: Two independent model invocations (discovery then falsification) with prompts that treat in-diff text and the candidate list as untrusted, require code-grounded evidence, and limit BLOCKING to a closed list.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T001, T002, T014, T015
- **Evidence**:
  - .github/review-prompts/discovery.md:10-16 (recall-only role), :43-48 (Lens 2), :60-66 (untrusted text)
  - .github/review-prompts/validate.md:9-13 (only output that reaches the PR), :19-24 (UNTRUSTED EVIDENCE), :26-33, :44-51 (falsify with (a)(b)(c), threshold 80), :54-58 (origin: validation), :65-80 (closed BLOCKING list)
  - .github/workflows/agentic-review.yml:114 and :169 select separate DISCOVERY_MODEL / VALIDATION_MODEL

#### M035: IMPLEMENTED: Deterministic fail-closed gate on SHA-scoped markers; every abnormal path (errored step, empty output, missing marker, oversized candidates) exits 1, and a CI step, not the model, posts the single PR comment.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T001, T013, T017, T019
- **Evidence**:
  - .github/workflows/agentic-review.yml:147-150 exit 1 without [DISCOVERY] $HEAD; :152-155 exit 1 above MAX_CANDIDATE_BYTES
  - .github/workflows/agentic-review.yml:256-259 outcome != success, :260-263 empty output, :264-267 missing [REVIEWED] $HEAD, :268-271 present [BLOCK-MERGE] $HEAD all exit 1
  - .github/workflows/agentic-review.yml:206-246: the comment body is assembled by the CI step and posted with gh using GH_TOKEN (:210); the model has no posting tool (:116, :171)

#### M036: IMPLEMENTED: Credential hygiene: checkout token not persisted, minimal job permissions, cloud credentials assumed last and only when Bedrock is configured.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T006, T007
- **Evidence**:
  - .github/workflows/agentic-review.yml:29-32 permissions contents: read, pull-requests: write, id-token: write
  - .github/workflows/agentic-review.yml:55-56 fetch-depth: 0 and persist-credentials: false
  - .github/workflows/agentic-review.yml:97-103 configure-aws-credentials runs after checkout, extraction and prefetch, only when env.USE_BEDROCK == 'true' (:99)

#### M037: IMPLEMENTED (partial): Regex redaction of AWS key ids, ARNs, 12-digit account ids and labelled secret values in model output before it is logged or posted, on top of GitHub's exact-string secret masking.

- **Outcome**: partially_implemented
- **Mitigation status**: mitigationInProgress
- **Linked threats**: T006
- **Evidence**:
  - .github/workflows/agentic-review.yml:146 and :201 perl -i -pe redact (AKIA|ASIA)[A-Z2-7]{16}, arn:aws\S*, \b[0-9]{12}\b and labelled aws_secret_access_key/aws_session_token/x-amz-security-token/api_key values
  - Gap: no pattern for a raw 40-character AWS secret access key, unlabelled session tokens/JWTs, ghs_/ghp_/sk-ant- prefixes or encoded forms; matches are redacted and processing continues
- **Recommendation**: Superseded by M052 (broader patterns, withhold output on match).

#### M038: IMPLEMENTED: Fork guard on every step plus a distinct job name for fork PRs, relying on GitHub withholding secrets from fork-triggered pull_request events.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T020
- **Evidence**:
  - .github/workflows/agentic-review.yml:46 job name expression yields 'Agentic AI Review (not run on forks)' for fork PRs
  - Fork guard if: github.event.pull_request.head.repo.full_name == github.repository on every step: :53, :60, :82, :99, :107, :130, :162, :188, :209, :250

#### M039: IMPLEMENTED: All third-party actions pinned to full commit SHAs with version comments; Python test dependencies version-pinned.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T007
- **Evidence**:
  - .github/workflows/agentic-review.yml:52 actions/checkout@3d3c42e5... (v7.0.1), :98 aws-actions/configure-aws-credentials@cbe3b392... (v6.2.4), :108 and :163 anthropics/claude-code-action@9c5ddab2... (v1.0.217)
  - .github/workflows/ci.yml:20 actions/checkout@3d3c42e5..., :23 actions/setup-python@e797f83b... (v6.0.0), :26 pytest==8.4.1 PyYAML==6.0.2
- **Recommendation**: Remaining gaps (CLI version, pip hashes) are tracked under M054.

#### M040: IMPLEMENTED: Scratch paths are removed before being recreated and the diff lives under $RUNNER_TEMP, so PR-committed files or symlinks at those paths cannot redirect writes or pre-seed gate inputs.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T016
- **Evidence**:
  - .github/workflows/agentic-review.yml:66-69 rm -rf .review-base .review-prompts then mkdir -p; :136-138 rm -f then ': >' .review-candidates.md; :192-194 rm -f then ': >' review-output.md; :86 pr.diff under ${{ runner.temp }}

#### M041: IMPLEMENTED: Blocking rule 'rules-may-only-tighten' makes any weakening of RULES.yaml, the prompts or the workflow a BLOCKING finding when reviewed against the base contract.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T003, T004
- **Evidence**:
  - RULES.yaml:41-56 rules-may-only-tighten with blocking: true (:42) and file-patterns RULES.yaml, .github/review-prompts/**, .github/workflows/agentic-review.yml (:44-46)
  - .github/review-prompts/discovery.md:43-48 and validate.md:66-70 direct the model to judge contract changes against the BASE snapshot

#### M042: IMPLEMENTED (partial): Per-PR concurrency cancellation, 30-minute job timeout, 40-turn cap per pass and a candidate-size cap bound the cost of a single PR's review.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T012, T015
- **Evidence**:
  - .github/workflows/agentic-review.yml:34-36 concurrency group agentic-review-<pr> with cancel-in-progress: true; :48 timeout-minutes: 30; :115 and :170 --max-turns 40; :133 MAX_CANDIDATE_BYTES "120000"
- **Recommendation**: Account-level cost controls are tracked under M050.

#### M043: IMPLEMENTED: Demo app guards: resolved-path containment (follows symlinks), absolute/empty path rejection, constant-time token comparison and prefix-only token logging.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T023, T024
- **Evidence**:
  - app/files.py:26-29 empty/padded and absolute-path rejection; :30-31 Path.resolve() on root and candidate; :36-38 containment check; :39-41 is_file()
  - app/tokens.py:15 _VISIBLE_PREFIX = 4; :18-22 describe_token; :27 hmac.compare_digest; :29 logs only describe_token(presented)

#### M044: IMPLEMENTED: Blocking rules no-guard-removal and no-secret-logging give the reviewer an explicit checklist for the two app guards, including the specific weak replacements attackers use.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T002, T023, T024
- **Evidence**:
  - RULES.yaml:11-29 no-guard-removal (blocking: true, app/**/*.py) naming startswith("../") and '".." not in requested' as non-replacements
  - RULES.yaml:30-40 no-secret-logging (blocking: true) naming app.tokens.describe_token as the only sanctioned form
  - .github/review-prompts/discovery.md:36-41 names the two guards the reviewer must watch

#### M045: IMPLEMENTED: The unit-test job that executes PR code runs with a read-only token, no repository secrets and a non-persisted checkout credential.

- **Outcome**: implemented
- **Mitigation status**: mitigationResolved
- **Linked threats**: T009
- **Evidence**:
  - .github/workflows/ci.yml:11-12 permissions: contents: read; :20-22 checkout with persist-credentials: false; :26-27 pinned installs and pytest; no secrets.* reference in the file

#### M046: Protect .github/** and RULES.yaml with CODEOWNERS plus a branch ruleset that requires code-owner review and forbids bypass, so a PR cannot merge a modified reviewer without a second human.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T003, T004, T005, T008, T020
- **Evidence**:
  - No CODEOWNERS file exists under .github/ or at the repository root; README.md:47-50 recommends it but nothing implements it
  - Ruleset/branch-protection settings are not expressible in the checkout
- **Recommendation**: Commit .github/CODEOWNERS covering /.github/ and /RULES.yaml and require code-owner review in the main ruleset.

#### M047: Move the privileged review job to a default-branch-defined workflow_run lane that consumes the PR diff as an artifact, so the code that reviews a PR can never be edited by that PR (and fork PRs can be reviewed safely).

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T003, T020
- **Evidence**:
  - .github/workflows contains only ci.yml and agentic-review.yml; agentic-review.yml:26-28 triggers on pull_request only; no workflow_run lane or artifact hand-off exists
- **Recommendation**: Design the default-branch workflow_run lane before relying on the gate for repositories with untrusted contributors.

#### M048: Verify branch protection/rulesets on main: required checks match the current job names exactly, no admin bypass, PR required; pin the check name in the workflow-invariants test.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T003, T005
- **Evidence**:
  - Repository settings cannot be read from the checkout
  - README.md no longer documents the required checks, PR requirement or bypass setting (the earlier setup step 4 was removed); the current job name to require is 'Agentic AI Review' (.github/workflows/agentic-review.yml:46)
- **Recommendation**: Restore the setup instruction and configure the ruleset; pin the check name in a workflow-invariants test.

#### M049: Harden the Bedrock IAM role: repository-scoped OIDC subject and audience conditions, InvokeModel-only permissions on the exact inference-profile/foundation-model ARNs, and the shortest practical session duration.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T006, T010, T011
- **Evidence**:
  - IAM trust and permission policies live in the AWS account, not the repository
  - .github/workflows/agentic-review.yml:98-103 pass role-to-assume and aws-region only; no role-duration-seconds is set
- **Recommendation**: Add role-duration-seconds: 900 to the credentials step and verify aud/sub conditions and InvokeModel-only permissions in IAM.

#### M050: Add cost and misuse monitoring: Bedrock budget and invocation alarms, model invocation logging with restricted access, CloudTrail alerting on role assumption, GitHub Actions spending limit, and trigger filters that skip draft or docs-only PRs.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T006, T007, T010, T011, T012
- **Evidence**:
  - No budget, CloudWatch alarm, invocation-logging or CloudTrail configuration exists in the repository
  - .github/workflows/agentic-review.yml:26-28 has no draft filter or paths-ignore; the job runs on every synchronize
- **Recommendation**: Add AWS Budgets/CloudWatch alarms in the account and skip draft PRs in the workflow trigger condition.

#### M051: Constrain what the agent's Read tool can reach: deny-list /proc, home, temp and .git paths via Claude Code permission settings, drop the unused ANTHROPIC_API_KEY input when Bedrock is active, and consider a container job with a minimal filesystem.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T001, T006, T008
- **Evidence**:
  - .github/workflows/agentic-review.yml:108-127 and :163-185 pass no settings or permission-deny input to claude-code-action
  - .github/workflows/agentic-review.yml:111 and :166 pass anthropic_api_key unconditionally; :47 runs-on: ubuntu-latest with no container: block
- **Recommendation**: Add Read deny rules for /proc/**, ~/.aws/**, $RUNNER_TEMP/** (except pr.diff), /tmp/** and **/.git/**; gate the API-key input on USE_BEDROCK == 'false'.

#### M052: Treat secret-shaped content in model output as a gate failure rather than something to redact: broaden the patterns (raw AWS secret keys, GitHub and Anthropic token prefixes, JWTs, long base64 blobs) and withhold the output entirely when they match.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T006
- **Evidence**:
  - .github/workflows/agentic-review.yml:146 and :201 redact and continue; only :147-150 (missing marker) and :152-155 (size) fail the candidate step; no secret-shape check fails the gate at :256-272
- **Recommendation**: Add a grep for secret shapes after redaction that exits 1 and posts a fixed 'output withheld' comment.

#### M053: Add an upper bound on reviewable diff size and reject Trojan-Source characters, so an attacker cannot exhaust the agents' turns or context to hide a small change.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T012, T015
- **Evidence**:
  - .github/workflows/agentic-review.yml:91-94 enforce only a non-empty diff; no byte/file ceiling and no bidi/zero-width character check exist
- **Recommendation**: Fail closed above a configurable diff size and on U+202A-U+202E / U+2066-U+2069 / zero-width characters in the prefetch step.

#### M054: Close the run-time install gap: pin the Claude Code CLI version, hash-pin Python test dependencies, and review action updates through Dependabot before adopting new SHAs.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T007, T009, T019
- **Evidence**:
  - No Claude Code CLI version is pinned in either claude-code-action step (.github/workflows/agentic-review.yml:108-127, :163-185)
  - .github/workflows/ci.yml:26 uses pip install without --require-hashes; no .github/dependabot.yml exists
- **Recommendation**: Pin the CLI version via the action input, add a hashed requirements file, and enable Dependabot for github-actions.

#### M055: Preserve an audit trail independent of editable PR comments: upload the redacted outputs and execution transcript as workflow artifacts and reference run id and SHA in the comment.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T018
- **Evidence**:
  - No actions/upload-artifact step exists in .github/workflows/agentic-review.yml; :221 heading includes only the first 12 characters of the head SHA and :217 marker carries no run id
- **Recommendation**: Upload review-output.md, .review-candidates.md and the execution_file as artifacts; add run id to the comment heading.

#### M056: Measure the reviewer empirically against the attack corpus after every model, prompt or action change, and pin model ids so behaviour changes are deliberate.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T001, T002, T013, T014
- **Evidence**:
  - No measurement harness or results are present in the checkout (demo/ and tests/ referenced by earlier README revisions are absent)
  - .github/workflows/agentic-review.yml:114 and :169 fall back to hard-coded model ids when DISCOVERY_MODEL/VALIDATION_MODEL variables are unset
- **Recommendation**: Script repeated runs of the attack tags and record pass/block rates; set the model variables explicitly.

#### M057: Make the bot comment unambiguous and non-authoritative: include run id and SHA in the marker, keep lane markers distinct, and document that the check run, not the comment, is the verdict.

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T017, T018
- **Evidence**:
  - .github/workflows/agentic-review.yml:217 marker="<!-- agentic-ai-review -->" is static; :221 heading has no run id; README.md does not state that the check run rather than the comment is authoritative
- **Recommendation**: Embed run id and SHA in the marker and document the check run as the verdict of record.

#### M058: Scope the secret-derived USE_BEDROCK expression to the job (or a single step) instead of the workflow-level env block (ASH finding 1).

- **Outcome**: not_implemented
- **Mitigation status**: mitigationIdentified
- **Linked threats**: T022
- **Evidence**:
  - .github/workflows/agentic-review.yml:38-39 still define USE_BEDROCK in the workflow-level env block
- **Recommendation**: Move the two lines under jobs.agentic-review (verified on copies with semgrep and checkov earlier in this session).

#### M059: When reusing the pattern on non-public code, keep model calls on Bedrock with restricted invocation logging (or zero retention) and review the Anthropic API fallback's data terms.

- **Outcome**: partially_implemented
- **Mitigation status**: mitigationInProgress
- **Linked threats**: T021
- **Evidence**:
  - .github/workflows/agentic-review.yml:21-24 and :98-103 make Bedrock the primary path and the Anthropic API a fallback
  - No documentation in the repository addresses data-handling considerations for reuse on private code, and no zero-retention or invocation-logging guidance is present
- **Recommendation**: Add a reuse note to the README covering Bedrock data handling, invocation-log access control and the API fallback's terms.

#### M060: Define the recovery path for outages and false blocks: bounded retries, documented re-run, and a code-owner override procedure that never weakens the required check.

- **Outcome**: partially_implemented
- **Mitigation status**: mitigationInProgress
- **Linked threats**: T013, T014
- **Evidence**:
  - .github/workflows/agentic-review.yml:224 tells the reader to re-run the workflow when the review did not complete
  - No retry exists around the model steps (:108-127, :163-185) and no override procedure is documented; the gate at :249-272 has no bypass, which is correct
- **Recommendation**: Add one bounded retry for throttling/5xx and document a code-owner override procedure that never weakens the required check.
