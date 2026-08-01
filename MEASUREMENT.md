# Measurement plan

## Baseline

Recorded at `2026-08-01T09:40:28Z`, immediately before repository preparation.

The local measurement command was:

```bash
node /home/income/bin/metrics.mjs
```

It reported `NO CHANGE` and `new-liquor-license-leads=1` for 30-day distinct users.

A direct anonymous request to the public Apify API at preparation time returned:

| Metric | Baseline |
|---|---:|
| Total users | 2 |
| Users, prior 7 days | 1 |
| Users, prior 30 days | 1 |
| Users, prior 90 days | 1 |
| Total runs | 18 |
| Public runs, prior 30 days | 8 |
| Successful public runs, prior 30 days | 8 |
| Failed / timed out / aborted public runs, prior 30 days | 0 / 0 / 0 |
| Reviews | 0 |
| Rating | 0 |
| Bookmarks | 0 |

Actor API endpoint:

```text
https://api.apify.com/v2/acts/rook-data-tools~new-liquor-license-leads
```

Pricing observed at the same endpoint was pay per event: `$0.01` per actor start and `$0.005`
per saved lead.

## Tagged outbound link

The README uses:

```text
https://apify.com/rook-data-tools/new-liquor-license-leads?utm_source=github&utm_medium=referral&utm_campaign=liquor_license_data_guide
```

The parameters describe the intended source. They are not evidence that Apify provides UTM
reporting, and this repository does not claim access to referral analytics.

## Future checks

At 7, 30, and 90 days after publication:

1. Run `node /home/income/bin/metrics.mjs` and save its timestamped snapshot.
2. Fetch the actor endpoint above and record the same fields in the baseline table.
3. In GitHub's repository Insights, record unique visitors, views, referring sites, and clones
   for the periods GitHub makes available. These owner-only traffic figures are not available
   from the anonymous repository API.
4. Record public GitHub stars and forks from:

   ```text
   https://api.github.com/repos/willowridge1234/new-liquor-license-data-guide
   ```

5. Compare deltas without claiming causation. Actor usage can change for reasons unrelated to
   this repository. Attribute traffic only when an actual referrer/campaign report supports it.

Do not backfill or estimate unavailable analytics.
