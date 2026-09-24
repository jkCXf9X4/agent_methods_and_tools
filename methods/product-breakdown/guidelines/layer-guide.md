# Layer Guide

Per-layer detail and worked routing examples for the seven layers. The boundary
rule in the breakdown's top-level `README.md` is authoritative when this guide
or [`storage-rules.md`](storage-rules.md) disagree; this guide expands it.

## Reading order

- The layers read top-down: Intent → Product → Architecture → Implementation →
  Verification → Operation, with Evolution holding candidates for change.
- Navigate the same way: top-level `README.md` → the layer index → the leaf that
  owns the concern. Indexes are navigation; leaves hold the current-state facts.

## The layers in depth

For each layer: what it is, what it holds, what it does not hold, and the
question to ask when deciding whether a fact belongs there.

### 1. Intent — `00-intent/` (ID-)

The product's reason to exist.

- **Holds:** scope, goals, mission, boundaries, the users or stakeholders the
  product serves, and the problem it exists to solve.
- **Example facts:** the operator persona; the in/out scope statement; the
  boundary between this product and adjacent systems.
- **Does not hold:** how something is built (Architecture, Implementation), or
  the detailed requirements of a capability (Product).
- **Ask:** "Why does this exist?"

### 2. Product — `01-product/` (PD-)

The promised deliverable.

- **Holds:** capabilities and requirements that others rely on; externally
  observable behavior; commitments to users and integrators.
- **Example facts:** an API surface contract promised to integrators; a required
  throughput figure; a user-facing capability.
- **Does not hold:** internal organizing decisions (Architecture), or how the
  code is written (Implementation).
- **Ask:** "What did we promise?"

### 3. Architecture — `02-architecture/` (AD-)

The organizing design.

- **Holds:** how the parts fit and interact; decomposition; data and message
  flow; interfaces between components; structural decisions.
- **Example facts:** component decomposition; the message flow between services;
  the interface contract between two components; a storage-format decision.
- **Does not hold:** specific files or scripts (Implementation), or the proof
  strategy (Verification).
- **Ask:** "How is the system organized?"

### 4. Implementation — `03-implementation/` (IMD-)

The concrete materialization.

- **Holds:** files, scripts, interfaces, and configs; concrete, code-level facts.
- **Example facts:** the CLI's config schema in `pb.toml`; a script's input and
  output contract; a config file's knobs.
- **Does not hold:** why a file exists (Intent, Architecture), or whether it is
  accepted (Verification).
- **Ask:** "Where is it, and what is in it?"

### 5. Verification — `04-verification/` (VD-)

Proof and acceptance.

- **Holds:** how each claim is checked; acceptance criteria; test strategy and
  the evidence that a claim holds.
- **Example facts:** the acceptance test for the checkout flow; the metric that
  proves a throughput requirement.
- **Does not hold:** the thing under test (its owning layer), or routine build
  steps (Operation).
- **Ask:** "How do we know it is true?"

### 6. Operation — `05-operation/` (OD-)

Routine build, release, and run.

- **Holds:** how the product is built, released, deployed, and run in normal
  operation; runbooks, release steps, routine maintenance.
- **Example facts:** the release steps; the on-call runbook; a routine
  maintenance window.
- **Does not hold:** one-off investigation or design rationale (its owning
  layer), or accepted design decisions (Architecture).
- **Ask:** "How is it run day to day?"

### 7. Evolution — `06-evolution/` (IMP-)

Candidates for change.

- **Holds:** not-yet-decided IMPs (evidence-backed pain or risk) and
  selected-but-not-implemented work.
- **Example facts:** an IMP proposing an alternative storage format, with the
  evidence behind it.
- **Does not hold:** current state (never restate it here), or accepted
  decisions (those live in owning leaves and `decisions/`).
- **Ask:** "What might change, and why?"

## Routing worked examples

Each change walks the same pipeline: idea → IMP → decision record (if
baseline-changing or cross-layer) → owning layer adopts → task → implement →
verify → IMP removed.

### Example 1: a new CLI flag that changes the config schema

- The concrete config knob is a file/config fact → **Implementation** owns it.
- If it changes the interface contract between components → **Architecture**
  owns that contract; Implementation defers to it by reference.
- If it changes a promised capability → **Product** owns the promise; defer by
  reference.
- Baseline change → a decision record with `layers: [implementation,
  architecture]`, each `state:` naming its owning leaf.
- Write the new state into the owning leaves in the same change, then regenerate
  the registers.

### Example 2: replacing the storage format

- Evidence-backed pain or risk → file an IMP under `06-evolution/selected/`.
- Cross-layer (format = Architecture, migration scripts = Implementation,
  rollout = Operation) → an accepted decision record is required before
  implementation.
- Owning layers adopt their slice of state; the IMP is removed once its
  resulting state is written; registers are regenerated.

### Example 3: clarifying who the product serves

- A pure scope fact → **Intent** leaf update.
- If it amends an accepted scope decision → also add a record superseding it.

## Cross-layer deferral pattern

- Keep the canonical statement at the layer owning the primary concern.
- Secondary layers get a link plus an explicit carve-out; never copy the fact.
- One fact has exactly one home; the registers fail fast if a link points
  nowhere.

## Common mistakes

- Restating current state in Evolution.
- Duplicating the same fact across two layers.
- Pushing design detail up (for example, config internals in Architecture).
- Writing rationale into an index instead of a decision record.
- Hand-editing a generated register.