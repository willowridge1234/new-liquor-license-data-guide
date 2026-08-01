# How to find new liquor-license data for B2B prospecting

New and pending liquor-license records can be useful signals that a restaurant, bar,
retailer, hotel, or entertainment venue is opening, changing ownership, or changing its
alcohol program. They are **signals, not verified sales leads**: an application may be
withdrawn, delayed, transferred, duplicated, or unrelated to your ideal customer.

This guide shows a reproducible way to find lawful public records, normalize them, remove
duplicates, qualify the remaining organizations, and use the result without turning a
public-record workflow into spam.

It is for sales operations teams and local B2B suppliers such as restaurant-equipment,
payments, insurance, signage, staffing, waste, linen, and food-service vendors. The workflow
is useful on its own and does not require a paid tool.

> Commercial disclosure: Rook Data Tools maintains this guide and sells a paid Apify actor.
> If you want an automated option, our [New Liquor License Leads actor][actor] currently
> supports Texas and California. It charges per run and saved lead; check the live page for
> current scope, pricing, and documentation. The rest of this repository explains how to do
> the work yourself.

[actor]: https://apify.com/rook-data-tools/new-liquor-license-leads?utm_source=github&utm_medium=referral&utm_campaign=liquor_license_data_guide

## Quick answer

A defensible liquor-license prospecting workflow is:

1. Start with the alcohol regulator for each state, province, or local authority.
2. Select **new applications**, **pending original applications**, or **newly issued
   licenses** rather than treating every active license as new.
3. Save the source URL, source record ID, record type, status, and event date with every row.
4. Normalize names and addresses, then deduplicate by stable license/application ID first.
5. Separate original applications from transfers, renewals, secondary permits, and events.
6. Qualify against a written territory and customer profile; verify important facts at the
   official source before outreach.
7. Use restrained, relevant, human-reviewed contact. Honor suppression and opt-out lists.

Do not assume that a filing proves a venue will open, that the applicant is the trade name,
or that a public phone number or email address grants consent for automated marketing.

## Where liquor-license records come from

Alcohol licensing is jurisdiction-specific. In the United States, the relevant authority is
usually a state alcoholic beverage control board or commission, but counties and cities may
also issue or publish local licenses, notices, hearings, or permit agendas. Elsewhere, the
authority may sit at the province, state, territory, council, or national level.

Look for these source types, in this order:

| Source | Useful signal | Typical limitation |
|---|---|---|
| Official open-data API or bulk download | Structured applications and licenses | Field names and update schedules change |
| Official daily/weekly report | New applications, issuances, or status changes | Often PDF, fixed-width text, or separate files |
| Official public inquiry/search | Current status and identity verification | May be designed for one-record lookups |
| Public meeting agenda or legal notice | Local hearings and protested applications | Unstructured and may contain sensitive personal details |
| Public-record request | Records not routinely posted | Delays, fees, exemptions, and reuse restrictions vary |

Two concrete official examples:

- [Texas Alcoholic Beverage Commission application status][tabc-status] provides a public
  path for checking pending original applications. TABC also documents how to obtain a list
  of pending original applications and publishes license data through its public inquiry/open
  data surfaces.
- [California Department of Alcoholic Beverage Control licensing reports][ca-reports]
  provides daily issued-license, new-application, and status-change reports, along with raw
  pending and active license data. California warns that reports can include duplicate and
  secondary license types.

[tabc-status]: https://www.tabc.texas.gov/services/tabc-licenses-permits/tabc-license-application-status/
[ca-reports]: https://www.abc.ca.gov/licensing/licensing-reports/

These are examples, not a claim of national coverage. Before collecting another jurisdiction,
confirm all of the following on the authority's current site:

- Is the record an application, issuance, renewal, transfer, surrender, or enforcement item?
- Is the date an application date, posting date, issue date, effective date, or update date?
- Does the authority publish a bulk file/API, or only a lookup interface?
- Are there terms, rate limits, public-record statutes, privacy notices, or commercial-use
  restrictions that apply?
- Does the state record omit a separate city or county license you also need?
- How are corrections and withdrawn applications represented?

Publicly accessible does not mean unrestricted. Follow the source's terms and applicable law,
collect only fields you need, avoid sensitive personal information, and document provenance.

## Define “new” before downloading anything

Teams often combine unlike events and then wonder why the list performs badly. Use an explicit
taxonomy:

- **Original pending application:** usually the earliest opening signal, but also the least
  certain.
- **Newly issued original license:** stronger evidence of approval, but it may arrive later in
  the buying cycle.
- **Person-to-person transfer:** may indicate a new operator at an existing venue; it is not
  necessarily a new location.
- **Premises transfer:** may indicate a move; verify both old and new addresses.
- **Renewal:** normally an existing operation, not a new opening.
- **Secondary/subordinate license:** can be another row for the same premises or application.
- **Temporary or event permit:** usually irrelevant to a permanent-location campaign.
- **Status change, surrender, or enforcement action:** a different business event; do not
  silently label it a new lead.

Keep `record_type` and the raw `status` in the normalized data. A downstream salesperson
should be able to distinguish an original application from a transfer without reopening the
source file.

## A reproducible weekly workflow

### 1. Write a source register

For each jurisdiction, record the authority, official URL, record type, publication format,
time zone, observed update cadence, stable identifier, terms/reuse notes, and the date you last
verified those facts. Do not write “daily” merely because a page looks current; use the
authority's own schedule or label the cadence as unknown.

### 2. Save an immutable raw snapshot

Store each download with an ISO date and a source label, for example:

```text
raw/2026-08-01_tx_pending_applications.csv
```

Also store a checksum and retrieval timestamp. Never overwrite last week's raw file. Immutable
snapshots let you explain why a row entered the CRM and re-run normalization after a schema
change.

### 3. Map into a small canonical schema

Use a schema that preserves evidence without pretending every authority publishes the same
fields:

| Field | Meaning |
|---|---|
| `record_type` | Your explicit event taxonomy, such as `pending_original` |
| `jurisdiction` | State/province/local authority code |
| `license_id` | Official license number, when present |
| `application_id` | Official application ID, when present |
| `license_type` | Raw official type/code |
| `status` | Raw official status or action code |
| `legal_name` | Applicant or owning entity as published |
| `trade_name` | DBA/trading name as published |
| `address`, `city`, `region`, `postal_code` | Licensed premises, not a guessed mailing address |
| `event_date` | Date tied to the event, with its meaning documented |
| `source_url` | Official page or record URL |
| `retrieved_at` | When your system obtained the record |

Blank values are better than invented values. Never infer a trade name from a legal entity,
guess an opening date from an application date, or turn an action code into a confident status
without documentation.

### 4. Normalize without destroying the raw values

Create comparison keys beside the original fields:

- Unicode-normalize and case-fold organization names.
- Collapse repeated whitespace and punctuation for comparison only.
- Standardize common street suffixes conservatively.
- Normalize postal codes as strings so leading zeros survive.
- Parse dates using the source's documented convention; reject ambiguous dates.

Keep the original spelling for display and audit. Normalization keys are tools for matching,
not corrected official facts.

This repository includes a dependency-free helper:

```bash
python3 tools/normalize_and_dedupe.py \
  examples/fictional_input.csv \
  /tmp/normalized.csv
```

It accepts the canonical columns above, adds `name_key`, `address_key`, and `dedupe_key`, and
keeps the first occurrence of an exact stable key. Run its tests with:

```bash
python3 -m unittest discover -s tests -v
```

The helper is intentionally generic. It does not fetch any source, bypass a site, enrich a
person, or decide whom to contact.

### 5. Deduplicate in layers

Use deterministic evidence before fuzzy matching:

1. Same jurisdiction + application ID.
2. Same jurisdiction + license ID + record type.
3. Same normalized premises address + normalized legal/trade name + event type.
4. Manual review for similar addresses or names within a narrow date window.

Do not merge solely because two businesses share an address; food halls, hotels, airports,
and mixed-use sites commonly have multiple licensees. Do not merge solely by owner name;
one operator can legitimately have several locations.

Maintain a crosswalk when an application later becomes a license. This avoids presenting the
issuance as an unrelated “new” account while preserving both events in the audit history.

### 6. Qualify the organization, not the mere existence of a filing

Write your ideal customer profile before looking at the list. A useful rule might be:

```text
In territory AND permanent on-premises food/beverage license
AND original application or new issuance
AND no existing customer/opportunity
AND our service is relevant before opening
```

Then classify each row:

- `review_now`: explicit fit and a time-sensitive reason to research.
- `verify`: plausible fit, but critical facts are missing or ambiguous.
- `exclude`: outside territory, renewal/event permit, duplicate, existing customer, or
  clearly irrelevant license type.

Good qualification checks include license type, record type, territory, premise type,
existing-account status, franchise/chain handling, and whether your offer is useful at this
stage. Weak shortcuts include assuming every LLC is a restaurant or every pending filing will
open soon.

### 7. Verify before contact

For any row selected for outreach:

1. Reopen the official record and confirm status.
2. Confirm that the address is the licensed premises.
3. Identify the organization through its own public business presence or a trusted business
   registry; avoid private personal profiles.
4. Check your CRM, suppression list, and prior opt-outs.
5. Record why the offer is relevant now.
6. Route uncertain or sensitive cases to a human.

The result should be a small review queue with provenance, not a mass-send file.

## Fictitious example output

Every organization, identifier, address, and date below is invented. It demonstrates the
shape only and is not lead data.

```json
{
  "record_type": "pending_original",
  "jurisdiction": "EX",
  "license_id": "",
  "application_id": "DEMO-1001",
  "license_type": "ON_PREMISES_DEMO",
  "status": "PENDING-DEMO",
  "legal_name": "Northstar Table LLC",
  "trade_name": "Juniper & Grain",
  "address": "101 Example Avenue",
  "city": "Sampleton",
  "region": "EX",
  "postal_code": "00001",
  "event_date": "2030-01-15",
  "source_url": "https://example.invalid/official-record/DEMO-1001",
  "retrieved_at": "2030-01-16T09:00:00Z",
  "name_key": "juniper grain",
  "address_key": "101 example avenue sampleton ex 00001",
  "dedupe_key": "application:ex:demo1001"
}
```

See [`examples/fictional_input.csv`](examples/fictional_input.csv) and
[`examples/fictional_normalized.csv`](examples/fictional_normalized.csv) for a duplicate,
a transfer, and an intentionally incomplete record. The reserved `.invalid` domain and the
fictional `EX` jurisdiction prevent accidental use as real prospects.

## Compliance and anti-spam guardrails

This is operational guidance, not legal advice. Laws vary by country, state, channel, caller,
recipient, and technology. Have qualified counsel review your program.

- **A public record is not marketing consent.** Do not treat publication of an applicant,
  phone number, address, or email as permission for automated outreach.
- **Email:** the US [FTC CAN-SPAM compliance guide][can-spam] says the law covers commercial
  email, including B2B email. Among other duties, use accurate headers and subjects, identify
  advertising as required, include a valid postal address and clear opt-out method, honor
  opt-outs promptly, and monitor vendors sending on your behalf.
- **Calls and texts:** automated/prerecorded calls and texts can trigger consent and other
  requirements under the TCPA and related FCC rules. Do not upload public-record phone numbers
  to an autodialer or bulk texting system without a channel-specific legal basis and process.
- **State and international rules:** state privacy/telemarketing laws and laws outside the US
  may be stricter. A US federal checklist is not a global compliance program.
- **Minimize data:** prefer business-level facts. Do not republish dates of birth, signatures,
  personal home addresses, personal phone numbers, or other sensitive fields merely because a
  source exposed them.
- **Suppress consistently:** maintain one durable do-not-contact list across representatives,
  tools, and vendors. A fresh public filing does not erase a prior opt-out.
- **Use relevance and restraint:** small batches, one clear reason for contact, honest identity,
  no manufactured urgency, no repeated sequences after silence, and no claims that you know the
  venue's opening date unless the business published it.
- **Audit vendors:** buying data or outsourcing sends does not transfer your responsibility.

[can-spam]: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Automated option: current verified scope

Rook Data Tools' [paid Apify actor][actor] is the easiest option if its current scope fits your
territory. As verified from the live Apify API on **2026-08-01**, it was public, supported Texas
and California, and used pay-per-event pricing of **$0.01 per actor start plus $0.005 per saved
lead**. Its public statistics showed **2 total users, 1 user in the prior 30 days, 18 total
runs, and 8/8 successful public runs in the prior 30 days**. It had no reviews or rating.

Those numbers are a dated baseline, not a promise of coverage, freshness, availability,
accuracy, or future pricing. Confirm the live actor page before relying on it. The actor returns
public-record fields; users remain responsible for qualification, verification, and lawful use.

## Measurement

The actor link uses only conventional UTM parameters:

```text
utm_source=github
utm_medium=referral
utm_campaign=liquor_license_data_guide
```

UTM tags make the intended referral identifiable where the destination supports them; they do
not prove that Apify exposes campaign analytics. No analytics integration is claimed.

The exact publication baseline and a repeatable future check are in
[`MEASUREMENT.md`](MEASUREMENT.md). Evaluate this repository by downstream change—actor users
and runs—alongside GitHub traffic data available to the repository owner. Stars alone are not a
revenue metric, and changes cannot be causally attributed to this guide without referrer data.

## Responsible contributions

Issues and pull requests that improve public-source documentation, generic normalization, or
compliance references are welcome. Do not submit real lead rows, personal information,
credentials, scraping bypasses, private methods, or unverified claims about a jurisdiction.

## License

Code in `tools/` and `tests/` is licensed under the MIT License. Documentation and fictitious
examples are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See
[`LICENSE`](LICENSE).
