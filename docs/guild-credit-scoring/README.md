# Guild credit scoring proposal and implementation readiness

Status: **Under consideration — documentation only; not approved for implementation or production.**

Recorded: November 22, 2026. Live model inspection and synthetic calculations: November 20, 2026. Refresh those observations before implementation. Tracking: [TGA-332](https://youtrack.thegig.agency/issue/TGA-332).

Alan's latest instruction is to preserve the analysis and be ready to implement in the next few days, while continuing consideration. Agreement with the direction is not implementation approval. Merging this documentation does not authorize scoring configuration changes, code implementation, deployment, historical rescoring, webhook replay, or advertising conversion replay.

## Decision summary

Proposed scope: Guild Purchase, Refinance and HELOC, across **all markets**, including submissions without a matched ad campaign ("Unmapped"). No Dallas-specific rule and no special first-time-buyer penalty.

| Estimated credit / input slug | Current X contribution | Proposed X contribution | Change |
| --- | ---: | ---: | ---: |
| Below 580 / `below_580` | 0 | **-6** | -6 |
| 580–619 / `580_619` | 3 | **0** | -3 |
| 620–679 / `620_679` | 6 | **6** | 0 |
| 680–739 / `680_739` | 8 | **8** | 0 |
| 740+ / `740_plus` | 10 | **10** | 0 |

Apply the negative contribution to the sum of X contributions, then floor the completed X at zero. Keep Y and all other question weights unchanged. Calculate `total_score = final X + Y`; calculate recommendations using those same final axes. Preserve the existing request and response shape, including `x_axis`, `y_axis`, `total_score` and `recommendations`.

This is a proposed points schedule, **not a total-score cap**. A 580–619 lead can still qualify if urgency is sufficiently strong; its contribution drops by three points rather than becoming negative. The original discussion of an extra deduction only for low down payment is not part of this proposed first release: the three-point reduction applies to that credit band across the three products, independent of down payment. Existing Purchase down-payment scoring remains intact.

## Why this is being considered

The original report described Purchase leads under 580 scoring 19–29 despite weak credit, often with under 5% down. Urgency answers lift them into top segments, while sales reported poor progression. Later evidence shows that some low-credit leads do progress; do not describe the entire group as producing no applications, no pre-approvals, or no value.

The live scoring engine currently gives below-580 credit **zero**, not negative, points. Purchase buying stage and timeline can contribute 10 points each, so maximum urgency produces X=20 without any credit contribution. Refinance and HELOC timeframe can contribute 10, reaching their qualification threshold without any credit contribution.

The scoring service is shared and scopes models by authenticated user/owner. The November 20 read-only inspection identified `guild-purchase`, `guild-refinance`, and `guild-heloc` as separate owners. Other tenants, including TMWC, must retain their behavior. Do not implement a global rule keyed solely on the `estimated_credit_score` field name. Revalidate tenant identities and model fingerprints in the target environment before any write; do not assume production IDs apply elsewhere.

## Actual tier rules: X and Y, not total score

| Product | Power Players | Fast Movers | Whales-in-Waiting | Window Shoppers |
| --- | --- | --- | --- | --- |
| Purchase | X >= 15 and Y >= 8 | X >= 15 and Y < 8 | X < 15 and Y >= 8 | X < 15 and Y < 8 |
| Refinance / HELOC | X >= 10 and Y >= 10 | X >= 10 and Y < 10 | X < 10 and Y >= 10 | X < 10 and Y < 10 |

Power Players and Fast Movers are treated as qualified. A total-score threshold such as 19 is not equivalent to qualification. Capping only `total_score` could leave X/Y-based segments and recommendations unchanged, preserving an incorrect qualified signal.

Most Purchase leads have low Y (about 4 on average); the supplied analysis says only about 3% reach Y=8. Consequently most qualified Purchase leads are Fast Movers. Their qualification is driven by X, rather than a Power Players designation.

## Evidence and provenance

1. **Live backend inspection, November 20:** Guild question choices, models, weights, value ranges and recommendation rules read via Django with `default_transaction_read_only=on`. Synthetic answers were passed only to calculation helpers in memory. No leads were created, updated, or sent. Credit contributions in the decision table were observed for all three Guild models.
2. **Landing integration inspection:** latest landing repository `main` fetched during that review, commit `32d2ccc` (abbreviated). Tier, after-hours and outbound behavior were read from source, not confirmed by new production submits. Repository: `The-Gig-Agency/guild-landing-system`. Local uncommitted documentation changes in its existing checkout were left intact.
3. **User-supplied market analysis:** [preserved market tables and discussion history](market-analysis-snapshot.md), scored leads since October 1; repeated patterns across SC, Atlanta, Dallas, St. Louis and Unmapped. Earlier snapshots report 524 HELOC leads; the final report reports 525. Do not mix denominators without reconciling the extraction times and exclusions.
4. **Final user-supplied funnel report:** [funnel-evidence-2026-11-20.md](funnel-evidence-2026-11-20.md), preserved byte-for-byte from Alan's attachment. It contains aggregate data and its own suggested scoring direction. Treat its suggested caps as reference proposals, not approval or an instruction to implement them.

The final report covers October 1–November 20, 2026: 4,857 scored leads (Purchase 4,288; HELOC 525; Refi 44). Salesforce "GoWith Total" exports were reported as current at November 20, 11:00 a.m. Eastern. Matching used submission time to the minute in Eastern time, page URL and UTM term, because Salesforce lacked email. Reported matches: engaged 690/807; credit events 113/131; pre-approved 19/24; under contract 12/14; funded 2/2. No source exports or matching implementation were independently audited in this review. Access to the Guild landing database through the available Supabase connector was denied; the outcome analysis remains user-supplied evidence, not independently reproduced production analytics.

### Main downstream evidence

| Purchase cohort | Qualified leads | Credit events | Pre-approved | Under contract | Funded |
| --- | ---: | ---: | ---: | ---: | ---: |
| Credit 620+ | 790 | 36 | 15 (1.90% of cohort) | 5 | 1 |
| Credit 580–619 | 589 | 21 | 0 | 0 | 0 |
| Credit below 580 | 311 | 16 | 2 (0.64% of cohort) | 1 | 0 |

Qualified below-580 Purchase leads engaged at 24% and reached credit events at 5.1%, versus 18% and 4.6% for qualified 620+ leads. Early engagement therefore does not establish equivalent downstream value. The 580–619 results support considering a modest penalty as well, despite no observed pre-approvals in its qualified cohort.

However, two qualified below-580 Purchase leads were pre-approved and one reached under contract. One nonqualified 580–619 Purchase lead also reached pre-approval and under contract. Preserve exceptions in the record; this is sales-priority scoring, not a loan-eligibility or denial rule.

HELOC had only five credit events, one pre-approval, three under contract and one funded in the supplied report. Refi had 44 leads, one credit event and one under contract. Applying the same credit schedule to them is a proposed cross-product policy, not an outcome-calibrated conclusion for each product. There is not enough evidence to optimize separate HELOC/Refi point amounts from those events.

### Market conclusion and data limitations

- Every supplied market showed below-580 leads qualifying through urgency. No evidence supports singling out Dallas. Earlier Purchase below-580 qualification rates ranged from 15% in Dallas to 26% in St. Louis; overall about 20%. HELOC below-580 qualification was about 72% overall, versus about 82% for 620+.
- "Unmapped" is an unmatched-ad-campaign bucket, including examples such as Meta, ManyChat or direct visitors. It is not a city and must not be excluded from the policy.
- HELOC credit-band rows sum to **517**, versus **525** in the final report header: eight records need reconciliation (do not assume their credit band or outcome).
- Product tables sum to **11 under-contract outcomes**, versus **12** matched in the report summary: one needs reconciliation.
- November leads have less time to mature; compare outcomes at matched 30- and 60-day observation windows before drawing strong conclusions.
- Minute-level matching can be ambiguous. Unmatched rows and match error may bias bands or markets differently; an 85% match rate does not guarantee uniform undercounting or unbiased conversion rates.
- Confirm event deduplication, unique leads versus scoring requests, stage definitions, and match confidence. Do not assume separately exported Salesforce stages form a perfectly nested funnel or sum them as unique conversions.
- Two matched funded outcomes overall cannot support a stable funded-rate model by product, market or credit band. Zero observed outcomes is not proof of zero future value or a causal effect of credit alone.

## Alternatives discussed, and the current preference

| Approach | Assessment |
| --- | --- |
| Cap total score at 12 | Rejected direction: does not fix X/Y-based qualification and can break score consistency. |
| Cap below-580 X at Purchase 12 and HELOC/Refi 7 | Earlier option: prevents qualification, but produces different rankings from the points proposal. Not the selected draft direction. |
| Cap Purchase 580–619 X at 14 | Suggested in the attached report: excludes that entire band from qualified regardless of urgency. Stronger than the modest three-point reduction discussed with Alan; not included in this draft. |
| Proposed -6 / 0 / 6 / 8 / 10 contributions, then X floor | Current preference for review: stronger below-580 penalty, modest reduction for 580–619, unchanged 620+ contributions. Implementation still pending approval. |

The proposal uses the existing `580_619` band (580–619). The conversational reference to "588 to 619" does not create a new band or omit scores 580–587.

## Expected score and segment impact

Under today's unchanged urgency weights, below-580 maximum X becomes **14 for Purchase** and **4 for Refi/HELOC**. All such leads fall below the qualified X threshold. This guarantee depends on current model weights, which must be covered by regression tests; future urgency increases can invalidate it.

Illustrative calculations using the November 20 live models (current scores reproduced in memory; proposed scores calculated arithmetically):

| Product / example | Credit | Current X / Y / total | Proposed X / Y / total | Segment change |
| --- | --- | --- | --- | --- |
| Purchase: signed agreement, within 30 days, $600–800k price, under 5% down | Below 580 | 20 / 9 / 29 | 14 / 9 / 23 | Power -> Whale |
| Same Purchase answers | 580–619 | 23 / 9 / 32 | 20 / 9 / 29 | Remains Power |
| HELOC: ASAP, $400–600k home, $100–250k mortgage | Below 580 | 10 / 16 / 26 | 4 / 16 / 20 | Power -> Whale |
| Same HELOC answers | 580–619 | 13 / 16 / 29 | 10 / 16 / 26 | Remains Power |
| Refi: ASAP, $250–400k balance, 7% current rate | Below 580 | 10 / 14 / 24 | 4 / 14 / 18 | Power -> Whale |
| Purchase: not started, 6+ months, under $200k, under 5% down | Below 580 | 3 / 3 / 6 | 0 / 3 / 3 | Remains Window; completed X floored at zero |

The Purchase below-580 example still totals 23, but is no longer qualified. Acceptance must check final X, tier and recommendation consistency, not require `total_score < 19`. If a separate absolute total threshold is wanted, that requires a new decision rather than quietly reintroducing a total cap.

### Cohort-level estimates, not a completed backtest

From the final Purchase table: 1,690/4,288 leads currently qualify (39.41%). Removing qualification from its 311 qualified below-580 leads alone yields 1,379/4,288 (32.16%): a **7.25 percentage-point decrease**. The 580–619 change would lower qualification further, but rounded averages cannot determine how many cross X=15.

For HELOC, 136 below-580 leads in the final table qualify. Using the header denominator, that is 136/525 = 25.90 percentage points. This is close to the earlier approximate 36% * 72% = 25.92% calculation. Do not present a precise post-change HELOC qualified percentage until the eight missing rows are reconciled; rounded earlier figures suggested roughly 78% -> 52% from the below-580 change alone. The 580–619 change could reduce it further.

Existing saved scores do not change merely by deploying a new policy. These are counterfactual estimates; this task has not rescored any historical leads.

## Integration and operational impact

The November 20 landing-source review found:

- `supabase/functions/_shared/lead-processing.ts` maps web and ManyChat answers to product-specific tenants and calls `/api/manage` action `domain.leadscoring.leads.create` with `allow_partial: true`.
- `lead-tiers.ts` derives segments from X/Y. Qualified signals use Power/Fast. Conversion values are Power=100, Fast=60, Whale=40, Window=5.
- The call center/Zapier path receives raw engine scores and tiers. Successfully scored leads are forwarded regardless of qualification, despite the high-intent secret names. Lowering scores therefore changes ranking and labels, not automatic suppression of delivery.
- The existing after-hours feature separately lowers X for paid-media signals, while the call center retains the raw engine result. A backend credit penalty becomes part of that raw engine result for both paths; it must not be applied a second time in the landing site. Revalidate the deployed settings and source before release.
- Advertising qualified-lead counts and conversion values will decrease; attribution/bidding comparisons must distinguish a scoring-definition change from a deterioration in actual lead supply. These point changes do not themselves alter platform campaign budgets or bidding settings.
- Historical scores, recommendation snapshots and derived tier/adjustment snapshots can drift if only some layers are backfilled. Any historical rescore needs an explicit plan for consistent snapshots and original submission times.
- Existing rescore modes may create scoring records and/or send webhooks or conversions. Their dry-run label alone is not proof of an in-memory counterfactual backtest. Inspect each call path before running it.

No landing API shape change is intended. Verify all web/ManyChat, call-center, Google/Meta and reporting consumers, including any total-score filters, before promising that no consumer changes are necessary. Shared scoring-reference documentation may need updating even when form code does not.

## Implementation plan, after approval only

Complexity: **Complex** when implemented, because this affects shared-tenant scoring and paid-media/customer-routing signals. This documentation task is a simple documentation-only change.

1. Re-fetch the backend and landing default branches; verify production release SHA, model owners and configuration fingerprints. Inspect current `AGENTS.md` instructions. Preserve concurrent Lovable work and use an isolated `codex/*` branch/PR.
2. Export and retain a private, timestamped snapshot of all three Guild models, ranges, weights and recommendation rules, plus fingerprints for non-Guild controls. Do not commit tokens or lead-level personal data. Record baseline aggregates for a fixed cohort and observation window.
3. Confirm the approved schedule, exact credit/unknown-value behavior and rollout scope. Existing valid input slugs stay unchanged. Missing credit on partial submissions, unknown slugs and malformed responses need an explicit tested policy; do not silently treat them as either excellent credit or below 580.
4. Extend the existing service/helper and tenant-scoped configuration paths. Keep the policy and score finalization outside route handlers. Inspect actual deployed source before choosing files: this checkout is not proof of production parity. Relevant existing paths include `backend/scoringengine/helpers.py`, `backend/scoringengine/models.py`, `backend/api/v1/scoringengine/views.py`, and `backend/control_plane/packs.py`.
5. Change the Guild credit contributions through a reviewed, idempotent configuration operation with expected-current-value checks. The existing value-range points are integers and support negative contributions; verify deployed validators and all write paths. Do not accomplish the penalty with a negative model weight.
6. Centralize finalization so create, update, managed create, recompute and recommendation evaluation use the same Guild-scoped final X. Apply `max(0, sum(all X contributions))` once after accumulation, then total=X+Y. Do not floor individual negative contributions or recompute recommendations from an unadjusted score. Repeated scoring/retries must not stack deductions.
7. A simple configuration-only negative range change does **not** provide the proposed final-X floor by itself. A scoped backend finalization change may be needed; do not globally clamp non-Guild tenants as a shortcut. Keep other scoring arithmetic and response semantics stable.
8. Add structured, non-PII audit/logging for policy version, tenant, old/new configuration fingerprint, score finalization and failure. Preserve the public response schema; record policy/version provenance internally without inventing new mandatory client fields.
9. Run the acceptance checks below and a side-effect-free historical backtest; attach impact aggregates and remaining caveats to a PR. Implementation approval does not authorize merging or deploying that PR.

## Acceptance and backtest checklist

- [ ] Exact credit contributions for all five bands across all three Guild owners; no changed 620+ scores or recommendations for otherwise identical valid inputs.
- [ ] Purchase below 580 + signed agreement + within 30 days, across every price/down-payment choice: final X <= 14 and not Power/Fast. A smaller down payment is not required for this protection.
- [ ] HELOC/Refi below 580 + ASAP, across value/equity/rate choices: final X <= 4 and not Power/Fast.
- [ ] Cover all urgency choices and missing/partial fields on both web and ManyChat paths. Define and test missing/invalid credit behavior before implementation is finalized.
- [ ] 580–619 contributes zero, not negative: X falls by up to three points after the floor; some strong-urgency leads remain qualified. Test crossing and noncrossing examples for each product.
- [ ] Floor at zero after all contributions; preserve decimals and total=X+Y. Test zero, negative pre-floor X, threshold boundaries (Purchase X=15/Y=8; others X=10/Y=10), repeat scoring and idempotency.
- [ ] Stored score, returned score, answer-point audit, recommendation rules and derived segments reconcile. Per-answer points can sum to a negative pre-floor X; the finalization adjustment must be explainable in internal audit.
- [ ] All scoring entry points agree. Regression controls for TMWC and other non-Guild tenants remain unchanged.
- [ ] Response fields/types and current payload slugs remain compatible. Recheck numeric/decimal handling and recommendation text, not merely JSON keys.
- [ ] After-hours adjustment runs exactly once after the backend credit policy; raw call-center and adjusted media tiers remain intentionally distinct. No change to qualification thresholds or Y.
- [ ] Reconcile HELOC missing rows, under-contract totals, Salesforce duplicate stages, join confidence and cohort maturity before claiming precise outcome impact.
- [ ] Backtest a frozen, deduplicated October 1–November 20 cohort, with a clearly recorded extraction cutoff, source, model fingerprint, timezone and unique-lead definition. Do not treat repeated scoring requests as new leads.
- [ ] Report old/new X/Y/total distributions, qualified rates, segment-transition counts and numbers of previously pre-approved/contract/funded leads demoted, by product, credit band, market and channel. Reconcile counts across slices. Include partial/unscored/missing-credit cases explicitly.
- [ ] Assess downstream conversion at matched 30/60-day maturity, by contact status where available; do not compare recent November leads directly with fully matured October leads.
- [ ] Backtest uses read-only data and in-memory calculations, writes no lead scores, creates no leads, and invokes no Zapier, Google or Meta delivery paths. Do not use the lead-create endpoint as a simulator.

## Approval, rollout and rollback gates

| Gate | Status / required authorization |
| --- | --- |
| Record analysis and proposal in this repo | Authorized by Alan on November 22; this PR only |
| Implement code/configuration change and backtest | **Not authorized yet**; Alan is still considering |
| Merge implementation PR | Separate, specific approval after tested diff and impact report |
| Promote to production / mutate live Guild configuration | Separate, specific release approval; define code/config order and rollback |
| Rescore existing leads / update historical landing snapshots | Separate approval defining cohort and persistence behavior |
| Resend call-center webhooks or advertising conversions | Separate explicit authorization; never a default of deployment or backtesting |

After the release gates are approved: validate in an isolated nonproduction environment with representative synthetic fixtures; choose a short coordinated release window; document a cutover time and policy version; deploy tested finalization support before enabling negative contributions (and only in the validated order); smoke-test through a no-send test path; compare live score/rate/error aggregates across products and markets. Avoid creating a period where negative X is exposed or recommendations disagree with final axes. A HELOC-first technical rollout can be considered because its qualification impact is largest, but the desired rule is market-independent; product staging and timing still require release approval.

Capture a rollback snapshot and rehearse the inverse code/config transition. Stop rollout on scoring errors, schema mismatches, non-Guild score changes or score/recommendation disagreement. Restore the recorded prior Guild contributions and compatible finalization code in the tested order. Rollback does not automatically rewrite historical scores or retract external conversions; handle those separately. Agree observation windows and success/rollback thresholds before release rather than inventing target qualified rates from immature outcomes.

## Open decisions when work resumes

1. Confirm the five-band points schedule, X floor, all-market/all-product scope and unchanged Y/thresholds. The document is a proposal, not implementation approval.
2. Confirm whether a moderate 580–619 reduction is still preferred over the attached report's blanket Purchase exclusion; do not combine the two silently.
3. Define missing/unknown credit behavior for partial callers, and verify active slugs/mappings and deployed-model parity.
4. Reconcile the evidence gaps and choose the backtest cohort/maturity rules, measurable success criteria and monitoring owner.
5. Choose new-leads-only release versus a separately reviewed historical rescore, and decide whether product staging is appropriate.
6. Obtain implementation approval, then review the tested implementation PR and separately authorize merge/release. Refresh this record if the policy changes.
