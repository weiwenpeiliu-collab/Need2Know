# Need2Know: Anonymous Benchmark Data

This archive contains an anonymized, dataset-only release of **Need2Know**, a controlled benchmark for implicit tool-need inference, retrieval, and task-conditioned information disclosure in LLM agents. It contains task inputs and reference data; **no model predictions, evaluation results, reviewer notes, or experiment logs** are included.

The underlying API-style schemas originate from an API-Bank-derived task/tool pool. The task requests and structured tool-return fixtures provided here are benchmark material, not records retrieved from live services. Names, identifiers, addresses, phone numbers, and emails occurring *inside synthetic examples* are deliberately part of the controlled evaluation fixtures; do not treat them as real personal records.

## Contents

| File | Entries | Purpose |
| --- | ---: | --- |
| `data/requests/implicit.jsonl` | 203 | Original implicit natural-language requests. Tool use is not explicitly requested. |
| `data/requests/explicit.jsonl` | 203 | Explicit main-benchmark requests aligned one-to-one with implicit requests; these are the **main benchmark's rewritten explicit prompts**, not the minimal-edit variants. |
| `data/requests/no_tool.jsonl` | 203 | Aligned generic requests that do not require fetching an external record; includes the intended `final_response` first action. |
| `data/task_definitions.jsonl` | 203 | One **shared** specification per task group: five candidate API schemas, Gold tool/arguments/required fields, low/medium/high controlled Gold returns, per-tier field disclosure policy, task type, and audience. |
| `data/non_gold_tool_responses.jsonl` | 812 | Four task-specific synthetic non-Gold responses per group; indexed by `task_id` and `tool_name`. |
| `data/evaluation/implicit_evidence_gap.jsonl` | 203 | Reference information-gap annotations and core evidence facets for implicit requests (**evaluation only**). |
| `data/evaluation/explicit_evidence_gap.jsonl` | 203 | Corresponding information-gap annotations for explicit requests (**evaluation only**). |
| `data/robustness/minimal_edit_explicit_51.jsonl` | 51 | Robustness subset with short task-specific retrieval/field prompts prepended to the **unchanged** implicit requests. |
| `data/robustness/retrieval_only_51.jsonl` | 51 | The same 51 IDs with a **generic** retrieval-only prefix; no task-specific evidence fields are named in the prefix. |
| `validate_release.py` | — | Offline integrity checks: aligned IDs, tool/Gold consistency, label/value consistency, number of fixtures, and robustness pairing. |
| `SHA256SUMS.txt` | — | SHA-256 hashes of release files (excluding the checksum file itself). |

## Data model and pairing

- Each JSONL line is an independent JSON object. The stable join key is `task_id`, e.g., `n2k_001`.
- The three main request files each contain **the same 203 `task_id` values** in the same order. They differ in `query` and request condition only. To evaluate a request, join it with `data/task_definitions.jsonl` on `task_id`.
- `task_definitions.jsonl` describes the **shared** environment across conditions; it must not be treated as content to show directly to the agent.
- Each task presents **five** candidate tools: one Gold tool and four distractors. The Gold tool schema belongs to `candidate_tools`; the annotated correct tool name, reference call arguments, and required fields are in `gold`.
- For correctly invoked Gold tools, choose one of `tool_results.low`, `.medium`, or `.high` as the returned JSON record. **Required field names and values are preserved across the three tiers, but extra protected fields (including their names) can differ by tier.** Do not assume every tier has an identical full field set.
- For distractor tools, match `(task_id, tool_name)` against `data/non_gold_tool_responses.jsonl` to obtain the synthetic returned content. The supplied file holds one task-scoped response per distractor; implement argument checking/tool invocation separately.
- `evidence_policy.{low,medium,high}` contains `required_visible_evidence` and `prohibited_sensitive_evidence`. Those are evaluation-only labels; the agent must not see the policy or the reference Gold answers before making its tool choice.
- `no_tool.jsonl` entries are intended to be answerable without consulting external records, even though the same set of candidate tools is available for the control condition. The shared Gold record is a reference fixture for alignment only.
- The two 51-task robustness files are **subsets**, not replacements for the 203-task main requests. `minimal_edit_explicit_51` prepends a targeted cue; `retrieval_only_51` prepends exactly: `Please first look up the relevant external information before answering.` These variants are separate conditions, not the main rewritten explicit prompts. The `request_type` of the retrieval-only file is normalized to `retrieval_only` for clarity; this differs from the original runner-compatible source's `explicit` value.

## Agent-visible vs. annotation-only information

**Agent-visible at the start of an episode:** the chosen request's `query` and the five `candidate_tools` schemas. The agent should receive a selected tool response only after an attempted tool call.

**Evaluator/simulator only:** `gold`, `tool_results` until called, `evidence_policy`, the information-gap annotation files, and the control's expected action. Do not expose any of these to the agent as extra hints.

The reference date stored uniformly in the original benchmark fixture metadata was **2026-10-10** (for interpreting relative-time expressions). It is documented here instead of repeated in 203 records.

## Counts and validation

- 203 task groups; 609 main request instances (203 per implicit, explicit, no-tool condition).
- 1,015 task–candidate-tool schema entries (5 per task group).
- 609 controlled Gold-tool output variants (203 × 3 tiers).
- 812 controlled non-Gold tool responses (203 × 4 distractors).
- 51 aligned groups each for minimal-edit explicit and retrieval-only robustness conditions.

Run from the extracted archive root:

```bash
python validate_release.py
```

`SHA256SUMS.txt` provides per-file hashes; on a system with `sha256sum` you can check with `sha256sum -c SHA256SUMS.txt`.

## Scope and limitations

- This is a **data-only** archive. The model runner, system/action prompts, API adapters, and evaluation/judge implementation are not supplied, so this archive alone does not reproduce published model results.
- The common task definition consolidates duplicated metadata from the three original full manifests. The requests and substantive tool schemas, Gold fixtures, and evidence policies are preserved without changing their values. Internal source IDs, redundant duplicate fixtures, provenance hashes, draft annotations, and local experiment-specific metadata were omitted.
- The `evidence_policy` labels are the original task-conditioned labels, not a claim that every possible audience interpretation is unambiguous.
- No license or redistribution permission was provided with the source archive; licensing and any upstream API-schema attribution requirements must be resolved by the release owner before public redistribution. This README does not grant usage rights.
