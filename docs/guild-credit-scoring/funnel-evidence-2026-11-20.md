# Lead scoring vs. Salesforce funnel, by credit band (for Codex)

**Window:** leads from Oct 1 to Nov 20, 2026 (4,857 scored leads: Purchase 4,288, HELOC 525, Refi 44).
**Salesforce source:** Guild's "GoWith Total" exports as of Nov 20, 2026 11:00 ET (Contacts Engaged, Credit Events, Pre-Approved, Under Contract, Funded).
**Join:** Salesforce has no email. Rows were matched to our leads by submission timestamp (to the minute, ET), page URL and UTM term. About 85% of Salesforce rows since Oct 1 matched (engaged 690/807, credit 113/131, pre-approved 19/24, under contract 12/14, funded 2/2). Rates below are slight undercounts.
**Caveat:** November leads have had little time to reach pre-approval or later stages. Counts past credit events are small.

Tier rules: Purchase qualified = X >= 15 (Power if Y >= 8 too). HELOC/Refi qualified = X >= 10 (Power if Y >= 10 too).

## Purchase: credit band x qualified

| Credit | Qualified? | Leads | Avg X | Avg Y | Engaged | Credit event | Pre-approved | Under contract | Funded |
|---|---|---|---|---|---|---|---|---|---|
| 620+ | Qualified | 790 | 18.9 | 4.1 | 18% | 4.6% (36) | **15** | 5 | 1 |
| 620+ | Not | 272 | 11.2 | 4.1 | 14% | 1.1% (3) | 0 | 0 | 0 |
| 580-619 | Qualified | 589 | 17.3 | 4.1 | 18% | 3.6% (21) | **0** | 0 | 0 |
| 580-619 | Not | 1,072 | 10.5 | 4.0 | 9% | 1.4% (15) | 1 | 1 | 0 |
| <580 | Qualified | 311 | 15.5 | 3.9 | 24% | 5.1% (16) | **2** | 1 | 0 |
| <580 | Not | 1,254 | 8.6 | 4.0 | 10% | 1.3% (16) | 0 | 0 | 0 |

## Purchase: by tier

| Tier | Leads | Avg X | Avg Y | Engaged | Credit event | Pre-approved | Under contract | Funded |
|---|---|---|---|---|---|---|---|---|
| Power Players | 69 | 19.6 | 10.2 | 26% | 10.1% (7) | 2 | 1 | 1 |
| Fast Movers | 1,621 | 17.6 | 3.8 | 19% | 4.1% (66) | 15 | 5 | 0 |
| Whales-in-Waiting | 61 | 9.5 | 10.3 | 20% | 0.0% | 0 | 0 | 0 |
| Window Shoppers | 2,537 | 9.6 | 3.8 | 10% | 1.3% (34) | 1 | 1 | 0 |

## Purchase: by market and credit

| Market | Credit | Leads | Avg X | Engaged | Credit event | Pre-approved | Under contract | Funded |
|---|---|---|---|---|---|---|---|---|
| SC | 580+ | 1,017 | 14.4 | 10% | 2.7% (27) | 6 | 3 | 1 |
| SC | <580 | 603 | 10.1 | 7% | 1.3% (8) | 2 | 1 | 0 |
| Atlanta | 580+ | 548 | 14.8 | 15% | 1.8% (10) | 1 | 1 | 0 |
| Atlanta | <580 | 255 | 9.9 | 20% | 3.9% (10) | 0 | 0 | 0 |
| Dallas | 580+ | 549 | 14.2 | 17% | 2.7% (15) | 1 | 0 | 0 |
| Dallas | <580 | 317 | 9.4 | 16% | 1.6% (5) | 0 | 0 | 0 |
| St. Louis | 580+ | 447 | 14.7 | 20% | 3.8% (17) | 6 | 1 | 0 |
| St. Louis | <580 | 255 | 10.5 | 18% | 2.7% (7) | 0 | 0 | 0 |
| Unmapped | 580+ | 162 | 14.1 | 13% | 3.7% (6) | 2 | 1 | 0 |
| Unmapped | <580 | 135 | 9.4 | 9% | 1.5% (2) | 0 | 0 | 0 |

## HELOC: credit band x qualified

| Credit | Qualified? | Leads | Avg X | Avg Y | Engaged | Credit event | Pre-approved | Under contract | Funded |
|---|---|---|---|---|---|---|---|---|---|
| 620+ | Qualified | 136 | 16.2 | 11.9 | 14% | 1.5% (2) | 1 | 2 | 1 |
| 620+ | Not | 30 | 7.3 | 10.9 | 7% | 0% | 0 | 0 | 0 |
| 580-619 | Qualified | 138 | 12.4 | 11.2 | 18% | 0.7% (1) | 0 | 0 | 0 |
| 580-619 | Not | 25 | 4.2 | 11.7 | 12% | 4.0% (1) | 0 | 0 | 0 |
| <580 | Qualified | 136 | 10.0 | 10.8 | 20% | 0.7% (1) | 0 | 1 | 0 |
| <580 | Not | 52 | 4.6 | 10.2 | 6% | 0% | 0 | 0 | 0 |

HELOC by market: engaged 4% (St. Louis) to 19% (SC); 5 credit events, 1 pre-approval, 3 under contract, 1 funded in total. Too few downstream events to separate credit bands.

Refi: 44 leads, 1 credit event, 1 under contract. Not enough to read.

## Findings

1. **Engagement and credit events don't separate credit bands.** Qualified Purchase leads under 580 engage (24%) and reach credit events (5.1%) at least as often as qualified 620+ leads (18%, 4.6%). Low-credit leads pick up and allow a pull, but don't progress.
2. **Pre-approval does separate them.** 15 of 17 qualified Purchase pre-approvals came from 620+ leads (1.9% of qualified 620+). Qualified 580-619: **0 of 589**. Qualified <580: 2 of 311 (0.6%).
3. **580-619 is a problem too.** Qualified 580-619 Purchase leads produced no pre-approvals despite 21 credit events. This argues for applying an X penalty to 580-619 as well, not just under 580.
4. **X still predicts engagement.** Qualified vs. not doubles engagement and roughly triples credit events in every credit band. The issue is that urgency answers outweigh credit, not that X is wrong.
5. **The pattern is the same in every market.** Under-580 Purchase leads produced 2 pre-approvals across all markets (both SC).
6. **HELOC needs more data.** Downstream volume is too thin to set HELOC caps from outcomes. Base them on the Purchase evidence plus credit-band logic, and revisit as data matures.

## Suggested direction for scoring

- Purchase: cap X below 15 for <580 (e.g. 12) **and** for 580-619 (e.g. 14), so neither can qualify on urgency alone. Keep 620+ unchanged.
- HELOC/Refi: cap X below 10 for <580 (e.g. 7). Apply a smaller deduction for 580-619, pending outcome data.
- Backtest on these cohorts before release, and check results against pre-approvals at 30 and 60 days.
