# Method: deep-academic-research

Grounds research-paper claims in **verified, citable primary literature**.
The output is a `findings.md` document that maps every claim to the specific
theorem/result that supports it, marks each citation's verification status,
flags what the paper may and may not claim, and issues a per-claim verdict
(`grounded` / `partially-grounded` / `open`).

Why: a paper's background/theory claims are only as strong as the citations
behind them. Training knowledge is not a citation; a phantom citation or a
wrong DOI is worse than no citation. This method makes the grounding
claim-driven, the verification two-axis (bibliographic existence vs
content-level confidence), and the verdict honest per claim.

Distilled from the 14-task theoretical-grounding wave in
`product-breakdown/01-product/4_background/T01_…/T14_…`.

## Contents

| Path | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Agent entrypoint: workflow, verification protocol, findings.md template, status framework, pitfalls checklist, quality gates |
| [`references/worked-example.md`](references/worked-example.md) | The T07 Seidel-Jacobi hybrid case: two-stage iteration identification and the partially-grounded verdict |

## Use it

1. **Decompose** the paper's claims into parallel theory areas (one task per
   area, claims enumerated first and mapped to repo anchors).
2. **Sweep** each area in parallel; verify every citation against primary
   indexes (Crossref/OpenAlex/Semantic Scholar/Open Library/arXiv/publisher
   pages); resolve DOIs and compare content.
3. **Synthesize** into a findings.md: Summary → Literature map → Gap analysis
   → Recommended citations → Status.
4. **Verdict** per claim: grounded / partially-grounded / open (plus refuted
   when the literature contradicts the claim), with the condition that would
   upgrade the verdict.

## Adopt it

Install the skill bundle:

```bash
python3 install.py --method deep-academic-research                                  # -> ./.agents/skills/
python3 install.py --method deep-academic-research --into ~/.config/opencode/skills # global
```

The skill is self-contained: no scripts, no config. The findings.md template
and verification protocol live in `SKILL.md`; the worked example lives in
`references/`.
