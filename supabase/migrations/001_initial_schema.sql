create extension if not exists pgcrypto;

create table products (
  id uuid primary key default gen_random_uuid(), category text not null,
  brand text not null, model text not null, canonical_name text not null,
  specifications jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (brand, model)
);
create table product_research (
  id uuid primary key default gen_random_uuid(), product_id uuid not null references products(id) on delete cascade,
  summary text not null, key_parameters jsonb not null default '{}'::jsonb,
  second_hand_checks jsonb not null default '[]'::jsonb, known_risks jsonb not null default '[]'::jsonb,
  sources jsonb not null default '[]'::jsonb, research_version text not null,
  refreshed_at timestamptz not null default now()
);
create index product_research_product_refreshed_idx on product_research(product_id, refreshed_at desc);
create table listings (
  id uuid primary key default gen_random_uuid(), product_id uuid not null references products(id) on delete cascade,
  source text not null, external_id text not null, url text not null, title text not null,
  price numeric(12,2) not null check (price >= 0), currency text not null,
  condition text not null, color text, location text, delivery boolean, description text,
  attributes jsonb not null default '{}'::jsonb, image_urls jsonb not null default '[]'::jsonb,
  raw_payload jsonb not null default '{}'::jsonb, first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(), active boolean not null default true,
  unique (source, external_id)
);
create index listings_product_active_seen_idx on listings(product_id, active, last_seen_at desc);
create table listing_snapshots (
  id uuid primary key default gen_random_uuid(), listing_id uuid not null references listings(id) on delete cascade,
  price numeric(12,2) not null, active boolean not null, observed_at timestamptz not null,
  unique (listing_id, observed_at)
);
create table sessions (
  id uuid primary key default gen_random_uuid(), stage text not null default 'discovery',
  requirements jsonb not null default '{}'::jsonb, selected_product_id uuid references products(id),
  message_summary text, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table search_runs (
  id uuid primary key default gen_random_uuid(), session_id uuid not null references sessions(id) on delete cascade,
  product_id uuid not null references products(id), query jsonb not null,
  sources_requested jsonb not null default '[]'::jsonb, sources_succeeded jsonb not null default '[]'::jsonb,
  status text not null default 'pending', error_summary jsonb not null default '{}'::jsonb,
  started_at timestamptz, finished_at timestamptz
);
create index search_runs_session_idx on search_runs(session_id, started_at desc);
create table recommendations (
  id uuid primary key default gen_random_uuid(), search_run_id uuid not null references search_runs(id) on delete cascade,
  listing_id uuid not null references listings(id) on delete cascade, rank integer not null check (rank > 0),
  score numeric(5,2) not null check (score between 0 and 100), score_breakdown jsonb not null,
  explanation text, created_at timestamptz not null default now(), unique(search_run_id, listing_id)
);
create index recommendations_run_rank_idx on recommendations(search_run_id, rank);
