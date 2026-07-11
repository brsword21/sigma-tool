# Ceneo New-Price Benchmark Design

## Understanding summary

- Add Ceneo as a Firecrawl-backed source.
- Fetch one Ceneo product page for the selected device model.
- Return only the current lowest advertised price for a new device.
- Use the result as a comparison benchmark for used OLX listings.
- Keep the benchmark outside the used-listing ranking.
- A Ceneo failure must not prevent OLX results from being returned.

## Assumptions and constraints

- The existing Firecrawl API key and 20-second timeout are reused.
- Each search run fetches at most one benchmark for one selected product.
- Results without a valid Ceneo product URL, title, and PLN price are rejected.
- No personal data is collected by the adapter.
- Firecrawl response parsing stays defensive because search payloads can expose fields in
  either the document or its metadata.
- The benchmark is stored on the search run and returned separately by `GET /runs/{run_id}`.

## Final design

`CeneoFirecrawlSource` is a dedicated benchmark adapter rather than a `ListingSource`. It
searches Firecrawl with a domain-restricted query, validates Ceneo product URLs, extracts a
price from structured fields or product-page text, and selects the cheapest valid result.
It returns a `NewPriceBenchmark` containing the product title, price, currency, URL, source,
and retrieval timestamp.

`SearchOrchestrator` runs product research, used-listing collection, and the Ceneo benchmark
concurrently. The benchmark is persisted in the `search_runs.new_price_benchmark` JSONB
column. It never enters listing normalization, filtering, or ranking. Ceneo errors are added
to the run's controlled error summary; successful OLX results remain available and make the
run partial rather than failed.

## Error handling and tests

- Reject non-Ceneo URLs and records without a parseable price.
- Prefer explicit structured price fields, then use conservative PLN text extraction.
- Return `None` when no valid benchmark exists rather than inventing a value.
- Cover mapping, cheapest-result selection, noise rejection, timeout/error isolation, run
  persistence, and API presentation with unit and integration tests.

## Decision log

1. Ceneo uses Firecrawl to stay consistent with the existing external-service setup.
2. Only one lowest new-product price is returned because other new prices add no value to
   the used-versus-new comparison.
3. The benchmark has its own domain model and does not implement `ListingSource`, preventing
   new products from affecting the used-listing ranking.
4. The value is stored on the search run, avoiding a new repository and table for the MVP.
5. Failures are isolated per source and remain observable through the existing error summary.
