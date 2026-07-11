alter table product_research
  add column if not exists confidence double precision not null default 0.5
    check (confidence between 0 and 1),
  add column if not exists data_gaps jsonb not null default '[]'::jsonb;
