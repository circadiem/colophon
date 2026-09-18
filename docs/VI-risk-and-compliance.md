<!-- Discovery deliverable VI. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Risk & Compliance Notes.

*The structural constraints that shape the product rather than sit beside it — practice limits, the buyer-side conflict, dealmaking timing, and source terms. Not legal advice; the register counsel works from.*

## 01 — The central conflict

*Colophon discovers that an author can get their rights back, and Colophon may want to buy those rights. Those two facts cannot sit inside the same conversation.*

This is the defining design constraint, and it is sharper here than in the music engagement, where the client already owned the catalog. Three consequences follow, and they are architectural rather than advisory:

- Independent counsel is structural. Any rightsholder Colophon approaches is told in writing, at first contact, to take their own legal advice. The product never tells an author whether to terminate.

- No filings. Colophon computes dates and shows evidence. It does not draft, assemble, serve, or record notices, and it does not produce documents intended for filing. That work belongs to the rightsholder’s lawyer.

- Entity separation, if the intel product ships. Selling availability intelligence while acquiring properties from the same population is a conflict a counterparty will eventually name. Decide the structure before the first subscriber, not after.

*Unauthorized-practice standards are state-specific and turn on whether the service applies law to a particular person’s circumstances. Generalized calculation and public-record research sits on the safe side of that line; personalized recommendation does not. Counsel should confirm the boundary in the operating jurisdiction before any author-facing surface exists.*

## 02 — Dealmaking timing

| **Constraint** | **Consequence for the product** |
|---|---|
| Inalienability | Termination rights cannot be bought, waived, or pre-assigned. No feature may imply a right can be optioned in advance of its effective date. |
| Third-party timing | A binding further grant to a new party is valid only after the effective date of termination. The pipeline models relationship stages, not contract stages, before that date. |
| Incumbent’s window | After notice is served, the original grantee may negotiate when nobody else can. Any target under notice is scored as contested, with the incumbent named. |
| Renegotiation trap | A re-signed deal with the incumbent can replace the old grant and extinguish the termination. Alert on any recorded new grant to an incumbent during a live window. |
| Channels A and B differ | Contractual reversion and lapsed options carry none of these constraints. Once rights are back with the author, a deal is a normal deal — another reason the non-statutory channels lead the roadmap. |

## 03 — Rights that do not come back

**i · Trademark overlay**  Character names and logos are often registered marks held by the publisher or a licensee. Copyright reverting to an author does not carry the marks. For a character-led children’s property this can be the difference between owning the book and owning the franchise.

**ii · The surviving adaptation**  A derivative work made under the old grant keeps being exploited after termination. A new adaptation competes with it and may face a rightsholder with an interest in blocking one.

**iii · The illustration chain**  If the art was work made for hire, the visual identity of the character never becomes available at all. Text-only recapture is a partial asset and must be scored as one.

**iv · Territory**  Recapture reaching worldwide rights was recently affirmed in one circuit and is under Supreme Court petition. Until it resolves, model territory as a flagged variable and never price a deal on the assumption.

## 04 — Data & privacy

- Source terms register. Every source carries its licence terms in the schema — non-commercial restrictions, attribution requirements, per-seat limits, anti-scraping clauses. A harvester cannot be written without its terms recorded first.

- Living people. Heir and estate research stays within public records: probate filings, obituaries, agency listings. No purchased personal data, no contact aggregation, no household or relative graphs.

- Retention. Personal records for shortlisted targets only, with a deletion path once a target is closed out.

- Outbound accuracy. Nothing leaves the system asserting clear title. Exports are evidence packets with tiers and dates, labelled as research, and are wrong sometimes by design — which is survivable only if the labelling is honest.

## 05 — Risk register

| **Risk** | **Severity** | **Mitigation** |
|---|---|---|
| Practice-line breach | high | No filings, no personalized recommendation, counsel referral at first contact, reviewed before any author-facing feature. |
| Conflict exposure | high | Written disclosure at first contact; entity separation decided before the intel product exists. |
| Wrong availability call | medium | Tiering surfaced everywhere, manual audit sampling, precision favored over recall. |
| Source-terms violation | medium | Terms register, licensed feeds, manual capture for gated trade sources. |
| Incumbent outbids | medium | Expected, not preventable. Lead time is the only edge; work the calendar years early. |
| Corpus bias | low | Award lists skew toward canonized titles. Deliberately seed under-adapted and historically overlooked catalogs alongside them. |

### Standing rule

Colophon produces leads, dates, and evidence. It never produces an opinion about someone’s rights.
