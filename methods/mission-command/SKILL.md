---
name: mission-command
description: Why parent agents brief delegated children with intent, end state, constraints, and freedom of action (uppdragstaktik / mission command). Read when a brief's why has been optimized away from the prompt.
---

# Mission Command (Uppdragstaktik) for Delegation Briefs

Durable statement of *why* parent agents should brief delegated children the way
they do, drawn from the Swedish Försvarsmakten leadership philosophy
**uppdragstaktik** (the Swedish term for *mission command*, German
*Auftragstaktik*). If the intent, end-state, or constraint guidance has been
optimized out of the live system prompt, load this skill to recover the full
reasoning.

## What mission command is

Uppdragstaktik is a **decentralized leadership philosophy**, not a command
structure. The Försvarsmakten describes it as: *ledning och beslut
decentraliseras så långt ut i organisationen som möjligt* — command and
decision-making are pushed as far down as the situation allows. It emerged in
the 19th-century Prussian army (after Jena, via Scharnhorst and Moltke) as the
answer to a fundamental problem: **no plan survives contact with the
situation.** When the conditions change mid-execution, the unit that must wait
for new orders is lost; the unit that can decide for itself survives.

The doctrine is simple in shape and hard in practice:

1. The superior states **what** must be achieved and **why** — the mission, the
   objective, and the intent.
2. The superior states the necessary **constraints** — resources, rules of
   engagement, limits, deadlines.
3. The **how is left to the subordinate** — full freedom of action within the
   intent.
4. The subordinate has the **mandate to decide on its own** when the situation
   changes, even if that deviates from the original plan.
5. The precondition for all of this is that the subordinate **understands the
   superior's intent** — because the intent, not the plan, is the anchor for
   correct autonomous decisions.

Swedish doctrine separates the *philosophy* (uppdragstaktik) from the *content
that makes it work*: **målbild** (the picture of the desired end state),
**syfte/avsikt** (the purpose), and **genomförandeidé** (the concept of how the
whole operation is intended to unfold). Together these let a subordinate answer
*"the original plan is now infeasible — what do I do instead?"* without calling
home.

## The commander's intent structure

Across NATO doctrine (US FM 6-0, UK JDP, Bundeswehr ZDv 10/1) the intent is
built from a few fixed elements. Each has a direct analog in a delegation brief:

| Element | Doctrine meaning | Why the subordinate needs it |
|---|---|---|
| **Uppgift** — mission | What must be accomplished | Gives the task itself |
| **Syfte** — purpose | Why this task exists in the larger effort | The decision criterion: when in doubt, choose the action that serves the purpose |
| **Målbild** — end state | The desired final condition ("what done looks like") | The target the subordinate steers toward when the path changes |
| **Genomförandeidé** — concept | How the whole effort is intended to unfold, so parts act in concert | Lets the subordinate keep its execution *compatible* with siblings |
| **Ramar** — constraints/restraints | Resources, handlingsregler (rules of engagement), boundaries, limits | Defines the legal/safe space the subordinate may operate in |
| **Handlingsfrihet** — freedom of action | The how is deliberately not prescribed | The explicit license to exercise judgment instead of asking |

The inverse — dictating both *what* and *how* in detail — is the failure mode
called *kommandotaktik* (directive/instructional control): it robs the
subordinate of initiative and makes the whole tree brittle to friction.

US doctrine (FM 6-0) states the operating principles behind this: *create
shared understanding, provide a clear commander's intent, exercise disciplined
initiative, use mission orders, accept prudent risk* — all resting on *mutual
trust*.

## The gap: intent withheld for encapsulation's sake

A delegation architecture deliberately gives a child **only** its brief —
*"nothing from your parent"*. That encapsulation is what keeps contexts shallow
and cheap. But mission command says a mission without intent is exactly the case
where a subordinate **cannot** make correct autonomous decisions:

- The child's plan hits friction → it has no end state to steer toward, so its
  options are: grind on the dead plan, fail, or escalate.
- A failed child is then recovered by the parent's abort-and-retry loop — the
  *most expensive* outcome, and precisely the one an intent block exists to
  prevent.
- Runtime safety caps (spawn limits, budgets, timeouts) act as *handlingsregler*
  but are **discovered by being hit**, not communicated up front — so children
  cannot self-regulate against them.

The intent is therefore not context *noise*; it is the **decision criterion**
that makes delegated autonomy safe and aligned. It is the same economics as
fresh-context theory: a few hundred tokens of intent up front buys insurance
against a failed child's full context + retry cost. Encapsulation should
protect the parent's context from the child — not deprive the child of the
parent's direction.

## Implications for a delegation brief

A brief should carry, alongside the task itself:

1. **A structured intent block** — purpose, end state, constraints, and the
   license to adapt, kept to a few sentences. A verbose intent becomes
   *kommandotaktik* by another name and defeats the fresh-context economy.
2. **Acceptance as contract, not advice.** "Done looks like X" is a stated
   field the child verifies against and the parent re-verifies against.
3. **A mandate to adapt + report back.** Explicitly: *if the situation changes,
   deviate as needed to honor the intent; report the deviation and why.* This
   turns the child's two bad exits (plow ahead / fail) into a third, aligned
   one.
4. **The ramar up front.** The child's own hard limits (token budget, timeouts,
   delegation caps) should be surfaced as constraints in the brief, not as
   surprises revealed on violation.
5. **Verify against intent, not plan-adherence.** The parent's verify step
   checks the outcome against the *end state*, not whether the child followed
   the original plan.

The discipline stays "minimal **and complete**": the brief must contain the
mission, the intent, the constraints, and the acceptance — and nothing else.

For a worked mapping onto one concrete harness (field names, prompt blocks, and
policy wiring), see [`guidelines/host-dynamic-harness.md`](guidelines/host-dynamic-harness.md).