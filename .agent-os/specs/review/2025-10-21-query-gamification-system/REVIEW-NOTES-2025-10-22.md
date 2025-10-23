Query Gamification System — Review Notes (2025-10-22)

Scope reviewed
- Files: README.md, srd.md, specs.md, tasks.md, implementation.md
- Goal: Reinforce query-first, multi-angle discovery by intercepting search_standards() with a lightweight, additive prepend

Verdict
- Concept: Strong and aligned with the orientation philosophy and agent-agnostic constraints. Intercepting search_standards() is the correct insertion point when you do not control the agent.
- Architecture: Pragmatic and minimal risk (in-process interceptor, zero deps, bounded memory, deterministic, graceful degradation).
- Tests/Quality: Good plan across unit/integration/performance/security, with explicit SLAs and rollback.

Strengths
- Agent-agnostic, server-only behavior shaping with no API/signature changes.
- Clear modular split (classifier, tracker, prepend generator, session extractor).
- SLAs and rollback are realistic (≤20ms overhead, ~1KB per session, single-file revert).
- Non-intrusive/default-off options considered (flaggable) and full test plan.

Issues to address and proposed fixes

1) Token budget inconsistency
- Observation: README targets ~85 tokens/query; FR-012 caps ≤500 tokens/task (5–10 queries). At 10 queries, ~850 tokens exceeds cap.
- Fix: Adopt an adaptive prepend policy + compact template to cap per-task tokens.

  Adaptive policy:
  - Query 1:
    - Header once + compact line
    - Example: 🔍 QUERIES=QUALITY | Q 1/5 U1 | 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜
    - Separator: ---
  - Queries 2–4:
    - Compact line only (no header): Q 3/5 U3 | 📖✓ 📍✓ 🔧✓ ⭐⬜ ⚠️⬜ | Try: ‘{topic} best practices’
    - Separator: ---
  - Completion (≥5 queries and ≥4 angles):
    - One-time completion line: Q 5/5 ✓✓✓✓ | ✅ Comprehensive discovery complete
    - Then suppress prepend for subsequent queries unless topic changes
  - Estimated total cost @10 queries: ≤250–350 tokens (within cap)

  Compact line template (≈25–40 tokens):
  - Q {total}/5 U{unique} | {angles} | Try: ‘{topic} {angle-pattern}’
  - Angles fixed order: 📖/📍/🔧/⭐/⚠️ with ✓ or ⬜

2) Security doc vs implementation mismatch (topic in prepend)
- Observation: Specs sanitize claim conflicts with suggestion including topic from user query.
- Fix: Allow topic, but sanitize strictly and update security docs.

  Sanitization guidelines:
  - sanitize_topic(query):
    - Keep lowercase [a–z0–9 -], collapse whitespace, trim to 24 chars
    - Fallback to “[concept]” if empty
  - Update Security section: “Sanitized subset of query terms may be included in suggestions; no raw user input is embedded.”

3) Session ID extraction robustness
- Risk: PID fallback can conflate concurrent sessions/transport multiplexing.
- Fix priorities:
  - Prefer server session/context ID (from existing session manager if available)
  - Else compose key: transport_id + pid (or connection hash + pid)
  - Last resort: “default”
  - Consider time-bucket suffix (e.g., 5-minute window) with pid fallback to reduce cross-conversation bleed if absolutely necessary

4) Prepend placement effects
- Risk: Prepend in results[0].content slightly reduces semantic purity of top chunk.
- Mitigations:
  - Use compact prepend; always follow with a separator line
  - Use a short tag “[QS]” or “Q:” prefix to make it ignorable by AIs if they choose
  - Inject only on first result; skip on empty results; header only once (query 1)

5) Classification accuracy/precedence
- Action: Define precedence and add negative keywords to reduce false positives (e.g., “where” in a “best practice” context).
- Tests: Cover ambiguous queries; assert deterministic classification outcomes.

6) Token measurement methodology
- Observation: Splitting by whitespace is not an accurate token proxy across models.
- Fix: Enforce a MAX_PREPEND_CHARS (e.g., 180 chars) guardrail and aim for empirical conformance to token budgets; keep internal token est. as advisory only.

7) Sticky completion cost
- Observation: Persistent completion message adds recurring cost after 5/5.
- Fix: Show completion once, then suppress prepend on subsequent queries. Re-enable prepend only if angles drop below 4 (topic shift) or new explicit topic is inferred.

Concrete implementation adjustments

- PrependGenerator:
  - Inputs: tracker, session_id, current_query
  - Compute: totals, unique, angles_covered
  - If total == 1: include single header + compact line; else compact line only
  - After completion criteria met once, mark session state as “completed” and suppress future prepends unless topic changes materially
  - Enforce MAX_PREPEND_CHARS; truncate safely if needed
  - Prefix tag “[QS] ” or “Q ” for quick model filtering/recognition

- Topic sanitization:
  - def sanitize_topic(query: str) -> str:
    - Lowercase; filter to [a–z0–9 -]; collapse spaces; trim to 24 chars; fallback to “[concept]”

- Session extraction:
  - def extract_session_id_from_context():
    - Prefer server-session id if available
    - Else: combination of transport/connection id + pid
    - Else: “default”
  - Provide hash_session_id for logs (SHA-256 → 16 hex chars)

- Feature flag:
  - ENABLE_QUERY_GAMIFICATION=true|false (environment/config), default true
  - Allows fast disable if any regression is observed

- Metrics:
  - Log prepend length (chars), state (header/compact/completion/suppressed), and whether sanitized topic was used
  - Track reduction in prepend after completion (suppression savings)

Tests to add/adjust
- Token/char budget compliance across states: header, compact, completion, suppressed
- Session identity separation under concurrent calls (simulated)
- Sanitizer properties (idempotent, deterministic, no disallowed chars, fallback)
- Classification precedence/negatives with ambiguous phrasing
- One-time completion: subsequent queries suppressed; re-enable only on topic shift
- Performance p95 with adaptive logic still ≤20ms end-to-end

Action checklist
- [ ] Implement sanitize_topic(query) and update security docs to reflect sanitized inclusion
- [ ] Implement adaptive prepend policy (header once; compact lines; one-time completion; suppression)
- [ ] Enforce MAX_PREPEND_CHARS guardrail and remove reliance on whitespace token counts
- [ ] Improve session_id extraction (prefer server session/context; robust fallbacks)
- [ ] Add feature flag ENABLE_QUERY_GAMIFICATION and document it
- [ ] Add metrics for prepend char length and suppression savings
- [ ] Expand tests: ambiguous classification, sanitization, concurrency, adaptive states, suppression logic
- [ ] Update specs.md/SRD to resolve token budget and security text inconsistencies

Effort delta
- Additional effort beyond current plan: ~2–3 hours
  - Sanitization + tests: ~1h
  - Adaptive policy + suppression + tests: ~1–1.5h
  - Session extraction improvements + tests: ~0.5h

Rationale alignment
- Preserves zero-dependency, in-process enhancement and agent-agnosticity
- Maximizes “knowledge per token” with adaptive/suppressed prepend
- Keeps server-side levers effective without controlling the agent
