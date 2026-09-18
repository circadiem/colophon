<!-- Discovery deliverable II. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Rights-Availability Logic Spec.

*The three reversion channels expressed as computable rules, resolving to one status per work, per right type, per territory.*

## 01 — The status model

Availability is not a property of a book. It is a property of a grant — and one book can carry several. Text and illustrations may sit in separate chains; publishing rights and dramatic rights are usually separate grants with separate clocks. The unit of computation is therefore the triple (work, right_type, territory), and every triple resolves to exactly one status.

```
EXCLUDED·WFH          work made for hire — no termination right exists, ever
PUBLIC·DOMAIN        term expired or renewal not made — no acquisition needed
NEVER·GRANTED        no evidence the right ever left the author  → approach directly
REVERTED·LIKELY      out-of-print or lapsed-option signals  → confirm, then approach
TERMINABLE·NOW       window open, notice can still be served in time
TERMINABLE·FUTURE    window computed, notice service opens on a date
LAPSED·WINDOW        window passed or notice deadline missed — permanently closed
GRANTED·ACTIVE       held and exploited  → monitor only
```

*Status carries a confidence tier and an evidence set at all times. A status without evidence is not a status; it is a guess, and the interface must show the difference.*

## 02 — Channel C · Statutory termination

### § 203 — grants executed by the author on or after 1 January 1978

```
window_start = if grant conveys the right of publication:
   min( publication_date + 35y , execution_date + 40y )
 else execution_date + 35y
window_end   = window_start + 5y
notice_service = effective_date − 10y  …  effective_date − 2y
last_serviceable_date = window_end − 2y   ← the real deadline
```

Most book publishing agreements convey the right of publication, so the dual-clock rule governs the majority of the corpus. The operative deadline is never the end of the window — it is two years earlier, because notice must precede the effective date by at least two years and be recorded before it. Colophon surfaces last_serviceable_date as the primary date and the window as context.

### Who holds the right

- The author. If deceased, a surviving spouse takes half and children and grandchildren take half per stirpes; termination requires more than half of the author’s termination interest.

- For a grant executed by two or more authors of a joint work, a majority of the authors who executed it. A picture book signed jointly by author and illustrator therefore needs both when there are two.

- Grants executed by heirs rather than by the author are outside § 203 entirely — a fact that has ended more than one reclamation attempt.

### § 304(c) and § 304(d) — pre-1978 grants

```
304(c): window = copyright_secured + 56y  …  +61y
304(d): available only if the 304(c) window expired before 1998-10-27
        and was not exercised → window = secured + 75y … +80y
```

This is more live than it looks. Works whose copyright was secured from 1968 to 1977 reach fifty-six years between 2024 and 2033 — the late-Sixties and Seventies picture-book period, arriving now. Anything secured before about 1963 has already run both clocks and should be routed to the public-domain test instead.

### The derivative works exception

A derivative work prepared under the grant before termination may continue to be exploited afterward, but no new derivative works may be prepared under the terminated grant. This is a feature, not a caveat: a book adapted once in 1994 can be adapted again by whoever holds the recaptured rights, while the old film keeps running in the background. Books in that posture score higher, not lower.

## 03 — Channel A · Contractual reversion

The fastest channel and the largest population, because it depends on the publisher’s own contract rather than on a statute. Colophon cannot read the contract, so it reasons from the conditions those clauses typically trigger on.

| **Clause archetype** | **Observable signal Colophon can compute** | **Tier** |
|---|---|---|
| Out of print | No edition in print; no ebook or audio edition offered; no reprint recorded in the last several years. | T3 |
| Availability / sales floor | Royalty-period sales below a contract threshold — invisible externally; inferred only from prolonged absence from trade channels. | T4 |
| Non-exploitation of subrights | Dramatic rights granted to the publisher but never licensed onward in the decades since. | T3 |
| Imprint dissolution | Publisher defunct or absorbed; catalog partially abandoned in the transfer. | T3 |

*Reversion under these clauses is almost always request-activated, not automatic: the right returns when the author asks and the condition is met. The finding Colophon produces is therefore “this author could likely get these rights back by asking” — which is a conversation, not a claim.*

## 04 — Channel B · Option lapse

Film and television options typically run twelve to eighteen months with one or two paid extensions. Exercise is rare. The lapse itself is never announced, so the signal is the absence of anything after the announcement.

```
years_since_announcement ≥ 5  and  no production credit
and  no renewal announcement  and  no development trace
  → REVERTED·LIKELY  (tier 3; promotes to tier 2 on author or agent confirmation)
```

A lapsed option is the best lead type in the system. Somebody with money already decided the book should be a film, did the diligence, and then failed for reasons that are usually about them and not about the book.

## 05 — Worked examples

### A · The missed window

Grant executed April 1986, book published September 1987, publication right conveyed. Window start is the earlier of 2022-09 and 2026-04, so 2022-09; window ends 2027-09; last serviceable notice date was 2025-09. Status: LAPSED·WINDOW. The § 203 route is closed forever — but Channel A remains fully open, which is exactly why a single-channel product would have discarded this book wrongly.

### B · The plannable one

Grant executed June 1991, published March 1992. Window runs 2027-03 to 2032-03; notice may be served now for effective dates from 2028. Status: TERMINABLE·FUTURE, notice window open. Eighteen months of relationship-building before anything has to happen — the case the calendar exists for.

### C · The two-chain picture book

Author and illustrator signed separate agreements with the same publisher in 1989. Two grants, two clocks, two terminating parties, and an illustrator agreement that may carry a work-made-for-hire recital as a supplementary work. Status: split — text TERMINABLE·FUTURE, art EXCLUDED·WFH pending document review. The film asset is usually the look, so a split status is a downgrade, not a partial win.

## 06 — Carried to counsel

- Whether a given illustrator agreement’s work-made-for-hire recital holds up as a supplementary work, and what evidence would settle it short of the contract.

- Territory. A recapture recently held to reach worldwide rights in one circuit is under Supreme Court petition; until that resolves, territory is modelled as a variable with a flag, never as a settled value.

- What a third party may and may not do before a termination’s effective date — the constraint that shapes the entire outreach sequence in VI.
