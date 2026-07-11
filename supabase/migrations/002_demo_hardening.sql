alter table recommendations
  add column if not exists tier text not null default 'top'
    check (tier in ('top', 'secondary')),
  add column if not exists recommended boolean not null default false;

create index if not exists recommendations_run_tier_rank_idx
  on recommendations(search_run_id, tier, rank);
