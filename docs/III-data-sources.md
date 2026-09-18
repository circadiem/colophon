<!-- Discovery deliverable III. Source of truth: Colophon Discovery Pack (CO·DISC / 2026), converted from the .docx. Where docs/PRD.md disagrees with this file, this file wins. -->

# Data Source & Access Assessment.

*What each source can prove, what it cannot, how it is obtained, and what it costs. Sources are rated by the strongest claim they support on their own.*

## 01 — The spine · Statutory records

The Copyright Office is the only source that produces tier-1 evidence. In June 2025 it replaced the Online Public Catalog with the Copyright Public Records System, carrying registration and recordation data from 1978 forward plus metadata for millions of applications from 1898 to 1945. A bulk portal offers roughly 22 million records in MARC and CSV — registrations, renewals and recordations — and the search interface runs on a public JSON API.

| **Source** | **Strongest claim it supports alone** | **Tier** | **Access** |
|---|---|---|---|
| Recorded transfers | Named party held a specified right as of the recordation date. Recordation is voluntary, so absence proves nothing — coverage skews to securitized, litigated, or corporate-acquired catalogs. | T1 | bulk + API |
| Recorded termination notices | A termination is under way, by whom, effective when. Recordation before the effective date is mandatory, so coverage here is near-complete — the one place absence is meaningful. | T1 | bulk + API |
| Registration records | Author, claimant, publication date, and the work-made-for-hire flag. A publisher as claimant implies a transfer; the WFH flag drives the first filter. | T2 | bulk |
| Renewal records (pre-1964) | Whether a pre-1964 work was renewed. Unrenewed means public domain — a path with no rights work at all. | T1 | bulk + Stanford set |
| Catalog of Copyright Entries | Pre-1978 registration and renewal detail not yet in the modern system. Digitized volumes require OCR and are noisy. | T2 | scan + OCR |

## 02 — Bibliographic backbone

| **Source** | **Use** | **Cost** | **Notes** |
|---|---|---|---|
| Library of Congress / MARC | Authoritative first-edition records, LCCN as a join key, illustrator credited separately from author. | free | Best source for the original publication date, which drives every clock. |
| Open Library | Edition-to-work clustering, ISBN coverage, cover images, subject tags. | free | Open licence; clustering needs correction for board-book reissues. |
| ISBN registry data | Imprint lineage, in-print status, format variants. | paid | Defer to month two; Open Library plus LC covers the seed corpus. |
| Award lists | Caldecott, Newbery, Coretta Scott King, Sibert and state lists as permanence and demand signal. | free | Small, clean, high-signal; hand-curated once. |

## 03 — Adaptation & deal trace

| **Source** | **Strongest claim it supports alone** | **Tier** | **Access** |
|---|---|---|---|
| Screen metadata | An adaptation exists, by whom, released when — which establishes that rights were exercised and that the derivative works exception is engaged. | T2 | API, attribution |
| Wikidata | Book-to-screen relations as structured triples; useful for seeding, thin in the mid-list. | T3 | free / SPARQL |
| Trade announcements | An option or purchase was made, by whom, when. The single richest unstructured source; the absence of follow-through is the lapse signal. | T3 | licensed feeds |
| Deal-report services | Publishing and film-rights deal reports with named agents on both sides — often the only place a subrights agent is identified. | T3 | subscription |
| Publisher rights guides | Rights explicitly listed as available, by title, published for trade fairs. | T2 | free PDFs |

*Terms of use govern here, not ambition. Screen datasets carry non-commercial restrictions, trade titles prohibit bulk scraping, and deal services licence per seat. Assume licensed feeds or manual capture for anything commercial, and store a source URL and capture date for every extracted fact.*

## 04 — Person & estate

**i · Death and survivorship**  Whether the author or illustrator is living decides who may terminate and how many parties must agree. Public indexes only; no purchased personal data.

**ii · Probate filings**  Names executors and successors in interest. County-level, uneven, and worth pulling only for shortlisted targets.

**iii · Agency and estate sites**  Often state plainly who handles dramatic rights — the cheapest route to the actual counterparty, and frequently the fastest way to end a research thread.

**iv · Trademark register**  Character marks reveal who believes they own the brand, and warn that a copyright reversion will not carry the marks with it.

## 05 — What no source can tell you

No public source contains the publishing agreement. Nothing external shows whether dramatic rights were carved out, what the reversion clause requires, or whether a side letter moved rights in 1997. Colophon is an inference engine over proxies: its honest output is a ranked set of leads with evidence attached and the next confirming step named. The agreement itself arrives one way only — somebody who has it hands it over, after a conversation rather than before.

### Sequencing

Everything free and bulk-downloadable comes first. Paid sources enter only when a specific tier promotion depends on them — and never before the corpus exists.
