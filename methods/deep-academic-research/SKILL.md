---
name: deep-academic-research
description: >
  Grounds research-paper claims in verified academic literature. Use when
  writing or reviewing a paper's background/theory sections, related-work
  positioning, literature reviews, or citation verification — when claims must
  be backed by citable primary sources, not training knowledge. Covers the
  decompose → parallel-sweep → verify → synthesize workflow, the findings.md
  document structure, the grounded/partially-grounded/open status framework,
  the verification protocol (Crossref/OpenAlex/Semantic Scholar/Open
  Library/arXiv/publisher pages), and the pitfalls checklist (phantom
  citations, wrong DOIs, category shifts, overclaiming). Use ONLY for
  grounding paper claims in literature; do not use for ordinary writing or
  experiment edits.
---

# Deep Academic Research

Ground a research paper's claims in **verified, citable primary literature**.
The output is a `findings.md` document that maps every claim to the specific
theorem/result that supports it, marks each citation's verification status,
flags what the paper may and may not claim, and issues a per-claim verdict
(`grounded` / `partially-grounded` / `open`).

This skill distills the methodology that produced the 14-task theoretical-
grounding wave in `product-breakdown/01-product/4_background/T01_…/T14_…`
(see `references/worked-example.md` for the T07 Seidel-Jacobi case).

## When to use

- Grounding a paper's background/theory claims in primary literature.
- Literature reviews and related-work positioning.
- Verifying citations (DOIs, author lists, venues, years, pages) before
  submission.
- Answering "is this claim citable, and with what source?"

## Workflow

### 1. Decompose into theory areas

Split the paper's claims into **parallel theory areas** — one area per
independent body of literature. Each area becomes a task (T01…T14 in the
wave) with its own `findings.md`. Enumerate the claims **first** (numbered
C1…C5, or mapped to repo anchors like `GAP-*` IDs, `decisions/*.md`,
`article/sections/*.tex`, `3_studies/*/1_methodology.md`). Grounding is
**claim-driven, not topic-driven**: a source with no claim mapping is not
added.

### 2. Run parallel literature sweeps

Sweep each theory area independently — delegate one orchestrator task per
area, with parallel sub-agents per sub-area. Each sweep:

- harvests candidate sources per claim;
- checks each candidate against multiple indexes;
- writes verified findings to scratch (child artifact IDs referenced in the
  parent file);
- returns a literature-map section for synthesis.

### 3. Verify every citation

Every bibliographic record is checked against primary indexes; DOIs are
resolved and compared against expected content; content-level results are
marked verified vs inferred/training-knowledge. See
[Verification protocol](#verification-protocol).

### 4. Synthesize into a findings document

Per area: literature map → gap analysis → recommended citations → dated
status verdict. See [findings.md template](#findingsmd-template).

### 5. Issue a status verdict

Per claim: `grounded` / `partially-grounded` / `open` (plus `refuted` when
the literature contradicts the claim). See
[Status framework](#status-framework).

## Verification protocol

### Indexes / APIs

| Index | Use |
|---|---|
| **Crossref REST API** | Primary DOI/record verifier; resolve DOIs, confirm titles/venues/volumes/pages/authors |
| **OpenAlex** | Existence checks, author/venue metadata, fallback when Crossref misses a record |
| **Semantic Scholar** | Existence checks, citation lookup, fallback authority |
| **Open Library** | Book records (no DOI); verify existence/edition/year |
| **arXiv** | Preprints and papers with arXiv IDs; verify the ID resolves to the right paper |
| **Publisher pages / full text / OA** | Depth-of-access qualifier: `(full text)`, `(abstract)`, `(paywalled)` |
| **Proceedings records** | JMLR/NeurIPS/PMLR/ACM proceedings for conference papers |
| **Wayback Machine** | Only for web pages that may have moved (e.g. ACM policy pages); not a citation authority |
| **DBLP** | Optional; may be unreachable (Anubis anti-bot) — document the failure and fall back to Crossref |

### How to check DOIs

- **Resolve the DOI and compare content** — a DOI that resolves to an
  unrelated paper is a wrong DOI (e.g. `schweigerSurvey` DOI
  `10.1016/j.simpat.2019.04.003` resolves to an evacuation-dynamics paper;
  correct is `10.1016/j.simpat.2019.05.001`).
- **Cross-check Crossref metadata** against the bib entry (title, author
  list, venue, year, pages).
- **Never fabricate DOIs.** If a book has no DOI, verify existence via Open
  Library or a review DOI, and say so (`[KNOWN — Open Library; no DOI]`).
- Record the DOI per row so the check is reproducible.

### Citation marking (two axes)

Mark **bibliographic existence** separately from **content-level confidence**:

| Mark | Meaning |
|---|---|
| `VERIFIED` / `V` / `KNOWN` | Bibliographic record confirmed via web this run (Crossref/OpenAlex/Open Library/publisher/Wayback) |
| `VERIFIED-WEB (full text)` | Record confirmed AND full text read |
| `VERIFIED-WEB (abstract)` | Record confirmed; only abstract accessible |
| `TRAINING-KNOWLEDGE` / `K` / `INFERRED` | From model knowledge, high confidence but not re-verified this run; spot-check before quoting |
| `UNVERIFIED` | No record found in any index; do not cite |
| `R` / `I` | Content-level: result read/confirmed vs inferred from domain knowledge |

Confidence levels: `HIGH (Crossref-verified)`, `MEDIUM (canonical textbook;
metadata from training knowledge + Open Library)`, `LOW` — always name the
verification method in parens, never a bare "verified".

### Verification hygiene rules

- **No fabricated DOIs; no unverifiable citations.** Phantom sources go under
  "Do NOT cite without primary confirmation" and are replaced with verified
  alternatives.
- **Document tool failures** (e.g. DBLP/Anubis) and fall back to an
  alternative authority.
- **Verify against primary records, not memory.**
- **Corroborate INFERRED items** via secondary sources where possible.
- **Distinguish bibliographic verification from content verification** — a
  `V/I` row is citable for existence but its content must be spot-checked
  before quoting.

## findings.md template

```
# T<n> Findings — <Theory Area>

## Summary
One-paragraph verdict up front: what is grounded, what is missing, what the
paper must do. Bold the status word.

## Literature map
| Source | Full citation | Specific result | Grounds which claim | Applies where | In bib? |
```

Each row is one source: full citation (authors, title, venue
`vol(issue):pages`, year, DOI/ISBN), the **specific theorem/result** (not the
paper's topic), the claim it grounds (C1…C5 or GAP-ID), the repo location
(tex file / decision / GAP-ID), and bib membership (`Yes (key)` / `No`).
Add a `Conf.` column when confidence varies per row.

```
## Gap analysis
Per claim: What the repo says → What the literature says → Recommendation.
Mark each gap: grounded / needs-precision / open.

## Recommended citations
Priority-ordered tiers: Must-add (core) / Should-add (supporting) / Optional
/ Already in bib (no action) / Do NOT cite. One-line justification per
source, bib key, and point-of-use mapping (which tex file / claim).

## Status: <grounded | partially-grounded | open>
Dated verdict paragraph: (i) what is grounded and by which sources,
(ii) what is not, (iii) the concrete editorial actions required.
```

## Status framework

| Verdict | Definition |
|---|---|
| **grounded** | Claim is a direct restatement of a verified primary result (e.g. "Literally the Eager–Zahorjan–Lazowska average parallelism W/D"). |
| **partially-grounded** | Mechanism/concept is grounded but (i) a specific parameter is ad-hoc and must be stated, or (ii) the claim is argued, not proven/measured, or (iii) a required condition is only partially satisfied. |
| **open** | No evidence exists in the paper or the literature for the specific claim (e.g. "specified nowhere"; "no theory justifies 40 evaluations"). |
| **refuted** | The literature actively contradicts the claim. |

Verdicts are **per-claim, not per-file**, dated, and always name the
condition that would upgrade the verdict (verify `ρ < 1`; add `n`/CI; state
the threshold). Distinguish **"concept grounded"** from **"value grounded"**:
a claim can be partially-grounded because the concept is citable but the
specific numbers/procedure are engineering decisions.

## Pitfalls checklist

- [ ] **Phantom citations** — a citation that exists only in training
  knowledge (e.g. Mätzig 1981, De Lellis & Slotine) is demoted to optional
  and gated on re-verification; the grounding story must not depend on it.
- [ ] **Wrong DOIs** — resolve every DOI and compare content; a DOI that
  resolves to an unrelated paper is wrong.
- [ ] **Author-list errors** — verify the author list against Crossref (e.g.
  "Gu & Asher" = Gu & Asada; Schweiger et al. has 7 authors, not 12).
- [ ] **Wrong venue/year/pages** — verify against Crossref (e.g. Lohmiller &
  Slotine 1998 is Automatica 34(6):683–696, not 1223–1241; Ramsay & Li 1998
  is JRSS-B, not JASA).
- [ ] **Category shifts** — a term may mean something different in the
  literature than in the paper (e.g. "strong coupling" is a
  numerical/algorithmic term, not a graph-theoretic label; SCC size is not a
  faithful proxy for numerical coupling strength).
- [ ] **Overclaiming** — catch claims the paper may not make (no named
  theorem for elementary arithmetic; no guarantee at 40 evals; no standard
  metric; no Fibonacci precedent). Supply recommended rewording.
- [ ] **Unverifiable sources** — no record in any index → do not cite, or
  replace with a verified alternative.
- [ ] **Known vs inferred** — mark what was not re-verified and require
  re-check before citing.
- [ ] **Mark confidence** — never a bare "verified"; name the method.
- [ ] **Wrong "grounds" mapping** — a real result may not support the claim
  it was cited for (e.g. Zhou & Ji 2022 bounds constrained kernelized
  bandits, not EI×PoF).

## Quality gates

- Every citation is verified or explicitly marked (VERIFIED /
  TRAINING-KNOWLEDGE / INFERRED / UNVERIFIED).
- No phantom citations; no fabricated DOIs.
- Gap analysis is honest: what is grounded, what needs precision, what is
  open — stated explicitly.
- Status is justified per claim with the condition that would upgrade it.
- Recommended citations are prioritized, keyed, and mapped to the point of
  use.
- The paper's overclaims are caught and flagged with recommended wording.
- A claim is done only when every assertion has a verified citation at its
  point of use.

## References

- `references/worked-example.md` — the T07 Seidel-Jacobi hybrid case: how it
  was identified as a two-stage iterative method and why it ended
  partially-grounded. Read when you need a concrete worked example of the
  full workflow.
