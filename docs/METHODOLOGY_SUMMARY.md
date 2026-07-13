# Methodology Summary — Family Office Intelligence Dataset

**Project:** Polarity IQ Differentiator — Task 1  
**Dataset:** 50 verified family office records  
**Primary Source:** FO-MAX Family Office Database (`FO-MAX-data-sample-2.0.xlsx`)  
**Research Period:** May–June 2026  
**Author:** Siddique Khan  

---

## Executive Summary

This document describes how 50 family office records were discovered, enriched, verified, and prepared for production RAG ingestion. The methodology prioritizes **evidence over completeness**: every field is either sourced from FO-MAX, cross-checked against public references, or explicitly marked as a gap. No contact data is invented where the source marks it `Hidden`.

From a fund manager perspective, the output is designed to answer three questions for each office:
1. **Who are they?** (entity, geography, sectors)
2. **Can I trust this?** (sources, confidence score, gaps)
3. **Why reach out now?** (recent signals where publicly available)

---

## 1. Discovery Process

### 1.1 Source Universe

| Source Type | Role in Discovery |
|-------------|-------------------|
| **FO-MAX Excel Database** | Primary universe — 111 family office rows in sample file |
| **Company Websites** | URL validation and entity confirmation |
| **SEC EDGAR / 13-F** | Cross-check for US investment vehicles (e.g., Bezos Exeditions) |
| **Foundation / IRS 990** | Cross-check for philanthropic family vehicles (e.g., Walton) |
| **Crunchbase / Press** | Secondary enrichment for well-known offices (Emerson Collective) |
| **LinkedIn** | Principal title verification where publicly listed |

### 1.2 Search Parameters and Filters

**Initial universe:** 111 rows in `FO-MAX-data-sample-2.0.xlsx` (rows 5–115, header row 4).

**Quality gates applied:**

| Gate | Criteria | Rationale |
|------|----------|-----------|
| Name present | Column B non-empty | No anonymous records |
| Entity type | Family office / family investment vehicle | Exclude pure PE funds miscategorized |
| Data completion | `data_completion_text` score recorded | FO-MAX internal quality signal |
| URL quality | `Highest` or `Medium` preferred | Reduces dead-link entities |
| Geographic diversity | Retain US, EU, Israel, Asia mix | Assessment requires global sample |

**Final count:** **50 records** selected (top 50 by data completeness and entity clarity).

### 1.3 Filtering Rationale

We rejected 61 rows for one or more of:
- Incomplete entity description
- Duplicate or ambiguous naming
- Missing website with low completion score
- Non-actionable stub records

The 50 selected offices represent a **production-ready subset** — sufficient for RAG demonstration while maintaining verification rigor.

### 1.4 Discovery Workflow

```
FO-MAX Excel (111 rows)
    → Python extraction (openpyxl)
    → Field normalization (31 columns)
    → Quality scoring (completion + URL quality)
    → Top 50 selection
    → output/family_offices_extracted.csv
    → Verification enrichment
    → output/family_offices_enriched_verified.csv
```

---

## 2. Enrichment Process

### 2.1 Base Fields (from FO-MAX)

Each record includes up to 31 fields:

- **Entity:** name, description, investment thesis, sectors, domain, website
- **Location:** street, city, state/region, country
- **Contact:** first/last name, full name, title, location, LinkedIn, email, phone
- **Quality:** validation period, data completion scores, URL quality, email validation codes

### 2.2 Enrichment Fields Added

| Field | Description |
|-------|-------------|
| `data_sources` | Comma-separated list of sources used |
| `verification_method` | How verification was performed |
| `confidence_score` | 0–99% composite score |
| `verification_date` | June 2026 |
| `gaps_noted` | Honest list of missing/unverified fields |
| `recent_signals_flag` | Whether 2025 activity was found |
| `recent_activity_signals` | JSON quarterly activity structure |

### 2.3 Investment Thesis Extraction

Thesis text is taken **directly from FO-MAX column 7** (`Investment Thesis`). No AI rewriting of thesis content for production records. Where thesis is blank (e.g., some private offices), the gap is recorded in `gaps_noted`.

### 2.4 Principal Identification

Principals are identified from FO-MAX contact fields (columns 17–22). Where FO-MAX marks contact data as `Hidden` (privacy policy), we do **not** infer emails or phone numbers. For Tier A offices, principal names are cross-referenced against public sources (Wikipedia, company leadership pages, press).

### 2.5 Sector Categorization

Sectors use FO-MAX's native taxonomy (column 8). No reclassification unless cross-source conflict is detected — in which case both values are noted in validation chains.

### 2.6 Recent Activity Tracking

Recent signals follow a **conservative policy**:

- **Tier A offices (6):** FO-MAX profile + public website/press cross-check
- **Tier B offices:** FO-MAX profile + website where `url_quality = Highest`
- **All others:** FO-MAX profile only; quarterly fields marked "No public signal independently verified"

We do **not** invent deal names, amounts, or dates without a cited source.

---

## 3. Verification Approach

### 3.1 Multi-Source Cross-Verification

| Tier | Offices | Method |
|------|---------|--------|
| **Tier A** | Walton, Emerson, Bezos, Cascade, Vulcan, Edmond de Rothschild | 3-source cross-check |
| **Tier B** | Highest URL quality + named principal | FO-MAX + website |
| **Tier C** | Remaining records | FO-MAX primary + completeness check |

### 3.2 Confidence Scoring (0–99%)

Composite score based on:

| Factor | Weight |
|--------|--------|
| FO-MAX URL quality (`Highest` +15, `Medium` +5) | Up to +15 |
| Data completion score | Up to +10 |
| Valid HTTP website | +3 |
| Named principal (non-Hidden) | +2 |
| Base score | 70 |

**Definition of "verified":** Entity name, geography, and at least one of {website, description, sectors} confirmed from FO-MAX with optional public cross-check.

**Definition of "not verified":** Contact email/phone marked Hidden; recent deal activity without press citation.

### 3.3 Gap Handling Policy

| Situation | Action |
|-----------|--------|
| Field blank in FO-MAX | Leave blank; note in `gaps_noted` |
| Field = `Hidden` | Do not populate; note privacy limitation |
| Conflicting sources | Prefer FO-MAX for structured fields; note conflict in validation chain |
| Unverifiable AUM | Record as "Not disclosed" — never estimate without source |

### 3.4 Source Reliability Ranking

1. FO-MAX verified database (primary)
2. Official company website
3. Regulatory filings (SEC, IRS 990)
4. Tier-1 press (Bloomberg, Reuters, company PR)
5. Aggregators (Crunchbase, LinkedIn) — confirmatory only

---

## 4. Quality Gates

### 4.1 Mandatory Fields

| Field | Required |
|-------|----------|
| `name` | Yes |
| `description` | Yes |
| `country` | Yes |
| `website` | Preferred (96% populated) |
| `sectors` | Preferred (84% populated) |
| `contact_full_name` | Preferred (98% populated) |

### 4.2 Consistency Checks

- Duplicate name detection (0 duplicates in final 50)
- URL format validation (`http` prefix)
- Integer casting for completion scores
- Column index alignment verified against Excel header row 4

### 4.3 Pass/Fail Criteria

| Metric | Threshold | Result |
|--------|-----------|--------|
| Record count | 50 | PASS |
| Name completeness | 100% | PASS |
| Description completeness | 100% | PASS |
| Overall field completeness | ≥80% | PASS (96.3%) |
| Duplicate records | 0 | PASS |

**Pass rate:** 50/50 records approved for RAG ingestion.

---

## 5. Limitations and Gaps

### 5.1 Difficult Data Categories

- **Direct contact email/phone:** Often `Hidden` in FO-MAX (expected for UHNW privacy)
- **AUM:** Not disclosed for many private family offices
- **Recent deal-level activity:** Sparse for non-public offices
- **Principal LinkedIn:** Frequently hidden or limited

### 5.2 Impossible-to-Verify Information

- Personal cell numbers for principals
- Non-public portfolio positions
- Unannounced co-investments

### 5.3 Recency Constraints

All structured data reflects **FO-MAX validation period 2025** as recorded in source file. Recent signals for Q1–Q4 2025 are included only where FO-MAX profile or public source supports them — not fabricated.

### 5.4 Fund Manager Implications

- **High confidence offices:** Use for direct outreach planning (Emerson, Walton, Paz Capital, Cascade)
- **Conditional offices:** Verify entity via website before CRM import (low URL quality offices)
- **Contact gaps:** Route outreach via website forms or LinkedIn — not guessed emails

---

## 6. Output Artifacts

| File | Purpose |
|------|---------|
| `output/family_offices_extracted.csv` | Raw 50-record extraction |
| `output/family_offices_enriched_verified.csv` | Full dataset with verification metadata |
| `docs/validation_chains.json` | Machine-readable 3-sample chains |
| `docs/THREE_RECORDS_VALIDATION_CHAIN.md` | Deep-dive human-readable validation |
| `docs/validation_report.json` | Automated quality report |

---

## 7. Conclusion

The methodology is **transparent, reproducible, and honest about gaps**. A fund manager can trust entity-level intelligence for all 50 records, treat contact fields as conditional, and use recent signals as timing hints only where confidence ≥80%. This is appropriate for a family office intelligence product where privacy constraints are structural, not methodological failures.
