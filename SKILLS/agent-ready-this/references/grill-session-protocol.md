# Material decision questions

Use an interview only to resolve a decision that changes the requested work. Inspect repository evidence and existing answers first, then give a recommendation. A generated question list is a starting point to review, not a script to recite.

## Gate

- `skipped`: evidence, prior decisions, and reversible defaults settle the active scope.
- `useful`: a reply improves fit or ordering; authorized independent work continues.
- `required`: a necessary answer is missing for a specific operation. Keep that operation pending.

State the reason and affected recommendation IDs. An unknown about a deferred protocol does not block clear guidance edits. Disabling the interview changes question presentation, not the unresolved state.

## Before asking

Check the shortest reliable evidence path: current request and prior answers, nearest instructions, manifests and CI, then relevant source, tests, and project docs. Ask only if the answer can change an active recommendation's scope, ownership, architecture, authority, exposure, or acceptance criteria.

A missing tool capability, failed inspection, or heuristic command gap is not automatically a product question. Try the appropriate local evidence source before asking the user to supply it.

## Ask one decision at a time

Use the available question tool or a short chat question. Put the highest-impact dependency first; offer a recommendation and concrete alternatives when useful. Respect the host's input limits. Default to one question at a time and wait for the answer before asking a dependent question. A requested batch may contain up to the helper's supported limit.

Each question should identify:

- its stable `G-XX` ID and the finding that raised it;
- the decision and affected recommendation;
- the current recommendation and its consequence;
- one question the user can answer;
- what remains pending if no answer arrives.

Example: an existing domain action already works outside the page. Explain why a headless interface may fit, then ask whether the requested agent use must work without an open page. Do not ask the user to invent a transport architecture.

After each answer, remove questions it settles or makes irrelevant. Stop when another answer would not change the work. A question budget is a ceiling, never a quota; the helper defaults to at most fifteen candidate questions.

## Reading the helper's output

The helper assigns rough materiality and severity from topic rules. These values are not measured product risk. Verify each against the request and source evidence before using it as a blocker. `next_round` lists the questions selected for presentation; `questions` also preserves unresolved candidates.

`--mode off` leaves unresolved questions and their gate in the output, but makes `next_round` empty. Do not report them as answered or present them anyway. Continue independent work and state any exact dependency that remains.

## Record settled answers

The input follows [known-context.schema.json](../schemas/known-context.schema.json):

```json
{
  "answers": [{
    "question_id": "G-12",
    "status": "answered",
    "value": "Use the verified resource-level authorization policy in docs/security.md.",
    "source": "explicit-user-answer",
    "confidence": "high",
    "notes": "Policy reviewed for the requested caller and resource."
  }]
}
```

Use `question_id`, not an invented `topic` field. Only `answered` records with a value and an evidence/user source suppress their mapped questions. `deferred`, `defaulted`, empty values, and safe-default sources remain unresolved. `known_topics` is an explicit list of already settled topics; populate it only from reviewed evidence or prior decisions.

Suppression prevents repeated questions. It does not prove authorization, ingest answers into the recommendation engine, or recompute final recommendations. The acting agent must review how each answer changes the proposed work and record that decision in the existing task record.

## Defaults and completion

For a reversible implementation choice, state a reasonable assumption and proceed within scope. For missing authority, preserve the current access boundary and keep the dependent action pending. Silence and elapsed time never authorize a change.

The interview is complete when active work has its required decisions and the remaining items are explicitly deferred, rejected, or blocked. Give the next concrete result; do not ask again for consent the user already supplied.
