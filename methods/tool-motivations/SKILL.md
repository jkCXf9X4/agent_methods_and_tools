---
name: tool-motivations
description: What each tool category is for and why, and how to choose between them. Read when a tool's motivation or choice guidance has been optimized away from the prompt.
---

# Tool Use-Cases and Motivation

Durable statement of *what each tool is for and why*. The optimized prompt lists
tools and gives terse guidance. When the motivation behind a tool, or when to
prefer it over another, has been optimized away, load this skill to recover it.

Tool names and exact capabilities differ per harness; this document speaks in
*behaviors* and *tool categories*. A host-binding appendix
([`guidelines/`](guidelines/)) maps each onto one harness's concrete tool names.

## Discovery

- **Enumerate files** — a cheap way to find which files exist before reading.
  Always prefer listing a directory over guessing paths. A listing that yields
  nothing is a signal the guess was wrong; ask rather than fabricate a path.
- **Search file contents** — by pattern, with an optional extension filter.
  Use when you need to locate code by symbol or behavior, not when a path is
  already known.
- **Consume a known file** — pull a specific file. Page through large files so
  you never pull an entire file into context. Read summaries, not bodies.

## Workspace

- **Persist a finding** — write a result to disk. Every material result must be
  persisted before the terminal outcome. Never report without a durable record.
- **Surgical in-place replacement** — of the *first* match. Use when you know
  exactly what to change and where; use a full write for fresh/whole content.
- **Run commands** — builds, tests, version control. It is a raw command
  executor, not an interactive shell. Use it to *verify* (run the test) and to
  *act* (create directories).

## Network

- **Fetch external content** — retrieve a resource. Restricted to safe
  destinations (no localhost/private ranges). For a single page, fetch it; for
  many pages, prefer delegating children to fetch in parallel.

## Coordination & control

- **Spawn a sub-agent** — the core tool: split work into a fresh, isolated
  worker. Always prefer delegation once a task needs several tool calls.
  Delegate everything you can, in parallel, in one turn.
- **Push an existing worker forward** — tell a *specific already-created* worker
  to do more or clarify its output. Prefer this over pulling its full output
  into your context.
- **Read live status** — the current state *and* partial progress of workers
  (or one by id). Consult it after any worker fails or lingers to see what
  already succeeded.
- **Abort a worker** — cancel a stuck/looping/rogue worker (optionally its whole
  subtree), preserving what it already wrote. The abort result embeds the
  salvaged partial work, so you immediately see what it produced before it died —
  the raw material for a targeted retry rather than a from-scratch restart.
  Aborted workers are never resurrected on their own.
- **Read a stored record by id** — read an archived result across a
  progressive-disclosure view (headline → short summary → technical). Verify
  workers by summary first.
- **Persist mid-run findings durably** — park a working file (or inline
  findings) into the durable store *during* the run, returning a stable id. The
  host only auto-creates a record at the terminal outcome, so without this any
  mid-run temp/finding is stranded as a loose scratch file.
- **Self-monitor context/budget** — read your own cumulative message/token
  counters and live-context estimate. The cache-friendly way to self-regulate:
  consult it when work grows repetitive (before delegating/dropping/compressing)
  instead of waiting for a per-turn observation that would zero the prompt cache.

## Context management

- **Compress** — summarize the conversation to reset context when it grows
  large. Aggressive, lossy; prefer dropping discrete stale turns for that.
- **Drop stale turns** — remove specific stale committed turns (results already
  on disk) to keep context bounded while preserving recoverability.
- **Restore** — recover a dropped turn's full content on demand.

## Termination

- **Report** — terminal; submit verified results with a concrete summary and the
  stored record ids.
- **Escalate** — terminal; a structural/design blocker on the worker's scope,
  raised to the parent. The parent owns the worker's outcome.
- **Fail** — terminal; an unrecoverable error. Everything failed *must* be
  retried or escalated; never silently abandon a failed worker.
- **Abort** — a *parent-side* abrupt stop of a worker (see "Choosing between
  similar tools"). Not a worker terminating itself; it lets the parent stop
  stragglers and recover their partial work for a retry.

## Choosing between similar tools

- **search vs consume**: search to *find*; consume to *read*.
- **enumerate vs search**: enumerate to *list*; search to *match contents*.
- **surgical edit vs full write**: edit for a targeted change; write for
  fresh/whole content.
- **delegate vs do-it-yourself**: a known target needing 0–1 calls → do it;
  anything non-trivial (several calls, chained discovery, unknown scope) →
  delegate. Under-delegation is a failure mode. Over-delegation is never a flaw.
- **verify vs trust**: never synthesize from the *return summary* alone; verify
  the durable record on disk. The summary is a preview; the record is the truth.
- **push vs re-spawn**: pushing drives the *same* worker forward; re-spawning
  creates a *fresh* worker. Prefer push when the worker is healthy and just
  needs more direction; prefer abort + re-spawn when it is stuck, poisoned, or
  structurally unable to finish.
- **status vs record read**: status tells you *how* a worker's run went
  (outcome, failure, done/pending, salvaged progress); the record read gets the
  *content* it produced. Use status to decide *whether/how* to retry; use the
  record read to consume what it succeeded in writing.
- **archive vs write**: write puts a byte-for-byte file on disk (for you and
  your workers to consume directly); archive promotes a file or findings into
  the durable store where it becomes discoverable, id-addressed, and
  provenance-linked. Write for scratch + cursor; archive for anything with
  ongoing value. Then delete the scratch copy in cleanup.