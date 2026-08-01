# Publication metadata and checks

This file records the intended GitHub settings so publication is reproducible.

- Repository: `willowridge1234/new-liquor-license-data-guide`
- Visibility: public
- Default branch: `main`
- Description: `A practical guide and CSV tool for finding, deduplicating, qualifying, and lawfully using new liquor-license records for B2B prospecting.`
- Topics: `b2b-sales`, `lead-generation`, `liquor-license`, `open-data`,
  `restaurant-leads`, `sales-prospecting`, `public-records`, `data-cleaning`
- Website: leave blank; the README contains the disclosed tagged commercial link

After publication, verify without authentication:

1. `https://github.com/willowridge1234/new-liquor-license-data-guide` returns HTTP 200.
2. The anonymous GitHub API shows `private: false`, the exact description, and all topics.
3. `README.md`, `MEASUREMENT.md`, both fictional CSVs, the tool, tests, and license render.
4. Every first-party and official external link resolves; the tagged actor link preserves its
   query parameters and lands on the correct actor.
5. A clean anonymous clone contains the same commit as the publish-ready artifact.
6. Run `python3 -m unittest discover -s tests -v` in that clone.
