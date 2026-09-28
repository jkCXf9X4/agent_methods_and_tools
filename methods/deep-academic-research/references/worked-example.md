# Worked example: T07 — the Seidel-Jacobi hybrid

This is the worked example from the theoretical-grounding wave. It shows the
full workflow applied to one claim: the paper's proposed hybrid scheduler
(Tarjan SCC decomposition → Gauss-Seidel on the condensation DAG → Jacobi
inside SCCs, run as a single outer sweep per communication step).

## Step 1 — Is it a known method?

The gap analysis answers directly:

> "**No — the exact combination is novel, but it is a special case of a known
> family.** The structure 'outer Gauss-Seidel sweep over an acyclic block
> graph, inner Jacobi iteration inside each cyclic block' is precisely a
> **two-stage (inner/outer) iterative method** (Lanzkron, Rose & Szyld 1990;
> Frommer & Szyld 1992) applied to the condensation DAG of the SSP-level
> graph."

The identification chain: the hybrid's architecture = two-stage iteration.
The table row for Lanzkron, Rose & Szyld 1990 is marked "**Core grounding
result.** Two-stage (inner/outer) iteration: an outer Gauss-Seidel sweep over
blocks with an inner Jacobi iteration inside each block converges for
M-matrices when both splittings are convergent. This is precisely 'Jacobi
inside SCC, Seidel outside'." Frommer & Szyld 1992 "Extends two-stage
convergence to H-matrices; gives conditions under which inner iteration need
only be approximate (fixed small number of inner steps still converges).
Grounds the 'fixed number of steps' inner-Jacobi option."

The same inner/outer architecture appears in four neighboring families:
**Multisplitting methods** (O'Leary & White 1985), **Waveform relaxation with
partitioning** (Lelarasmee et al. 1982; White & Sangiovanni-Vincentelli
1986), **Dynamic iteration for coupled DAE systems** (Arnold & Günther 2001;
Miekkala & Nevanlinna 1987), and **Asynchronous iterations** (Chazan &
Miranker 1969; Baudet 1978).

What is genuinely novel is scoped precisely:

> "What is genuinely novel in the paper is the *application context*
> (co-simulation master scheduling over an SSP-level graph) and the
> *single-sweep semantics* (one outer Seidel pass per communication step,
> inner Jacobi run to a fixed count or tolerance). No prior co-simulation
> paper was found that combines Tarjan SCC decomposition with
> Seidel-outside/Jacobi-inside scheduling; the closest relatives are WR
> partitioning (circuit simulation) and iterative-coupling masters (which
> iterate the whole system, not per-SCC). **The novelty claim is defensible,
> but it must be positioned as 'a two-stage iteration specialized to
> co-simulation scheduling', not as an ungrounded invention.**"

## Step 2 — Termination criterion

Two defensible options, both grounded:

1. **Residual-based (recommended).** Stop the inner Jacobi loop when the
   successive-difference residual falls below a tolerance tied to the
   communication-step error budget: `‖x^(k+1) − x^(k)‖ < tol` with
   `tol = C·h^p` (h = communication step, p = local order). Justification:
   Banach contraction error bound `‖x^k−x*‖ ≤ (q^k/(1−q))‖x¹−x⁰‖` (Banach
   1922; Ortega & Rheinboldt 1970, Thm 12.1.2); Kelley (1995) gives practical
   successive-difference criteria with safety factor.
2. **Fixed step count (acceptable, with justification).** Because Jacobi
   converges linearly with factor `ρ` (spectral radius of the block-Jacobi
   iteration matrix), a fixed count `k ≥ log(tol)/log(ρ)` achieves the
   tolerance. Frommer & Szyld (1992) show two-stage methods tolerate
   approximate inner solves, so a small fixed count is theoretically safe
   *provided* `ρ < 1` is verified. The paper's "until convergence/fixed
   number of steps" phrasing is therefore principled **only if** the
   contraction condition is checked; otherwise the fixed count is arbitrary.

The honesty gate on the single-sweep semantics:

> "The outer Seidel pass needs no termination criterion in the paper's design
> (one sweep per communication step), but note that a single sweep is a
> **non-converged iterate** of the outer iteration — the coupling error
> analysis of Benedikt et al. (2013) applies, and the paper should state this
> explicitly rather than implying the hybrid 'converges' per step."

## Step 3 — Convergence conditions

> "**Strong connectivity of the SCC does not imply convergence** — a cyclic
> graph can have `ρ ≥ 1`. The paper's reference loop converges because the
> open-loop gain `k_{C→B}k_{B→C} = 0.4125 < 1` (`50_methodology.tex`), which
> is exactly the contraction condition for the 2-node loop; the synthetic
> SCC-dominant families must verify the same condition per family or their
> results are scheduler stress cases, not convergence evidence."

Three-level structure of the conditions: linear case (`ρ(B⁻¹C) < 1`;
sufficient: M-matrix / strictly diagonally dominant / SPD with
`2D − A ≻ 0`), nonlinear case (Banach contraction or Ortega–Rheinboldt), and
the outer level ("the condensation DAG is acyclic by construction (Tarjan
1972), so Gauss-Seidel over SCCs is always well-defined and converges for any
consistent ordering when the block iteration is convergent (Varga 1962). This
is the paper's soundest structural claim.").

## Step 4 — Per-claim verdicts

| Claim | Verdict | Grounding |
|---|---|---|
| Tarjan SCC decomposition; Seidel outside, Jacobi inside | **Grounded (structurally)** | Tarjan 1972; two-stage iteration (Lanzkron et al. 1990; Frommer & Szyld 1992); Varga 1962 |
| Hybrid combines both advantages | **Partially grounded** | Seidel propagation advantage: Arnold 2010, Kübler & Schiehlen 2000; Jacobi parallel loop handling: O'Leary & White 1985, Chazan & Miranker 1969. The *combination* benefit is argued, not proven |
| Sub-stepping/interpolation improves convergence | **Partially grounded** | WR windowing theory (Lelarasmee 1982; Miekkala & Nevanlinna 1987); unmeasured in paper |
| Hybrid convergence properties | **Open** | No executable implementation; convergence requires contraction conditions that are verified per-system, not guaranteed by the hybrid structure itself |

## Step 5 — Why it ended partially-grounded

> "The hybrid is a novel application of a well-established method family
> (two-stage iteration over an SCC condensation DAG). Its structural claims
> are grounded; its convergence claims require per-system contraction
> conditions that the paper partially satisfies (reference loop gain < 1) but
> has not verified for the synthetic SCC-dominant families; its benefit
> claims (sub-stepping, interpolation, combined advantage) are grounded in WR
> theory but unmeasured, consistent with the threats-to-validity admission of
> no executable implementation."

**The verdict logic in one sentence:** the *architecture* is grounded (it is
a known method family), the *structural* claim is grounded (condensation DAG
acyclicity), but the *convergence* and *benefit* claims are only partially
grounded because they depend on per-system conditions the paper has not
verified and on measurements the paper has not made — and the file is
explicit that the paper's own threats-to-validity section already admits the
missing implementation. Also notable: **none of the 20 recommended citations
were in the bib** ("None of the theory sources are in
`article/bibliography.bib`"), and the one training-knowledge source (Mätzig
1981) was demoted to optional pending re-verification.

## Recommended citations (priority order, excerpt)

1. **Lanzkron, Rose & Szyld 1990** — two-stage iteration; the single most
   important grounding for "Jacobi inside SCC, Seidel outside".
2. **Tarjan 1972** — SCC decomposition; cite wherever the Tarjan step is
   mentioned.
3. **Varga 1962** — block Jacobi/Gauss-Seidel convergence.
4. **Lelarasmee, Ruehli & Sangiovanni-Vincentelli 1982** — waveform
   relaxation; cite for the sub-stepping/interpolation claim.
5. **Miekkala & Nevanlinna 1987** — WR convergence and window-length
   dependence.
6. **Ortega & Rheinboldt 1970** — nonlinear fixed-point convergence.
7. **Banach 1922** — contraction mapping; cite for the principled termination
   criterion.
8. **Frommer & Szyld 1992** — H-splittings and approximate inner solves.
9. **Arnold & Günther 2001** — dynamic iteration for coupled DAE systems.
10. **Benedikt, Watzenig & Hofer 2013** — non-iterative coupling as truncated
    fixed-point iteration; cite in `77_threats_to_validity.tex`.

Already in bib (no action): `gomesSurvey`, `kueblerSchiehlen`,
`schweigerSurvey`, `fmiStandard`, `sspStandard`.
