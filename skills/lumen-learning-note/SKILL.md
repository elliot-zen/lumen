---
name: lumen-learning-note
description: Use when a user has finished studying a chapter or topic and wants to record what they learned plus open questions into a Lumen-powered knowledge note.
---

# Lumen Learning Note

## Overview

Use this skill when the user wants to turn a completed study session into a structured note stored through Lumen.

This skill is for the `learning_note` flow only. It collects the chapter title, learned points, and open questions, then calls Lumen's API.

## When to Use

Use when:
- The user says they finished learning a chapter or topic
- The user wants to record study notes, review notes, or learning questions
- The user wants the note saved into their Lumen + Obsidian workflow

Do not use when:
- The user is just brainstorming what to learn
- The user wants a generic journal entry
- The user has not actually studied anything yet

## Required Payload

Send a `POST` request to:

```text
http://127.0.0.1:8000/learning-note
```

With JSON shaped like:

```json
{
  "type": "learning_note",
  "topic": "ES",
  "chapter_title": "Async Iteration",
  "what_i_learned": [
    "for await...of iterates async values",
    "async iterables are useful for streaming results"
  ],
  "questions": [
    "When should I use streams?",
    "How do async generators propagate errors?"
  ],
  "source": {
    "kind": "codex_session",
    "title": "ES learning notes"
  }
}
```

Rules:
- `type` must be exactly `learning_note`
- `topic` must be non-empty
- `chapter_title` must be non-empty
- `what_i_learned` must contain at least one non-blank item
- `questions` must contain at least one non-blank item
- `source` is optional but recommended

## Workflow

1. Confirm the user actually finished learning something specific.
2. Extract:
   - topic
   - chapter title
   - learned points
   - open questions
3. Build the JSON payload.
4. Call the Lumen API.
5. Read the response.
6. If a `job_id` is returned, poll:

```text
GET http://127.0.0.1:8000/jobs/{job_id}
```

until the status becomes one of:
- `succeeded`
- `retryable`
- `failed`

## Response Handling

Successful initial acceptance looks like:

```json
{
  "job_id": 1,
  "status": "pending",
  "accepted_new": true,
  "dedupe_key": "..."
}
```

Job status looks like:

```json
{
  "job_id": 1,
  "status": "succeeded",
  "retry_count": 0,
  "note_path": "ES/Async Iteration.md",
  "last_error": null
}
```

Interpretation:
- `pending`: accepted, waiting for worker
- `processing`: worker is running
- `succeeded`: note created successfully
- `retryable`: temporary failure, can retry later
- `failed`: terminal failure

## Example cURL

```bash
curl -X POST http://127.0.0.1:8000/learning-note \
  -H "Content-Type: application/json" \
  -d '{
    "type": "learning_note",
    "topic": "ES",
    "chapter_title": "Async Iteration",
    "what_i_learned": [
      "for await...of iterates async values",
      "async iterables are useful for streaming results"
    ],
    "questions": [
      "When should I use streams?",
      "How do async generators propagate errors?"
    ],
    "source": {
      "kind": "codex_session",
      "title": "ES learning notes"
    }
  }'
```

## Common Mistakes

- Sending a blank `questions` array
- Sending a generic summary instead of concrete learned points
- Recording a topic before the user has actually studied it
- Treating `202 Accepted` as "note already written" instead of "job accepted"

## Copy / Install

To use this skill in another agent setup, copy this folder:

```text
skills/lumen-learning-note/
```

into that agent's local skills directory.
