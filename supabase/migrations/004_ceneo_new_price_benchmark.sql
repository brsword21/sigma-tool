alter table search_runs
  add column if not exists new_price_benchmark jsonb;
