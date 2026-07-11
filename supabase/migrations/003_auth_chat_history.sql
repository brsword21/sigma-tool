alter table public.sessions
  add column if not exists user_id uuid references auth.users(id) on delete cascade;

create index if not exists sessions_user_updated_idx
  on public.sessions(user_id, updated_at desc)
  where user_id is not null;

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.sessions(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null check (char_length(content) between 1 and 10000),
  created_at timestamptz not null default now()
);

create index if not exists messages_session_created_idx
  on public.messages(session_id, created_at, id);

alter table public.sessions enable row level security;
alter table public.messages enable row level security;

grant select, insert, update, delete on table public.sessions to authenticated;
grant select, insert, update, delete on table public.messages to authenticated;

drop policy if exists "Users can read own sessions" on public.sessions;
create policy "Users can read own sessions"
  on public.sessions for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users can create own sessions" on public.sessions;
create policy "Users can create own sessions"
  on public.sessions for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users can update own sessions" on public.sessions;
create policy "Users can update own sessions"
  on public.sessions for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "Users can delete own sessions" on public.sessions;
create policy "Users can delete own sessions"
  on public.sessions for delete to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Users can read messages from own sessions" on public.messages;
create policy "Users can read messages from own sessions"
  on public.messages for select to authenticated
  using (
    exists (
      select 1 from public.sessions
      where sessions.id = messages.session_id
        and sessions.user_id = (select auth.uid())
    )
  );

drop policy if exists "Users can create messages in own sessions" on public.messages;
create policy "Users can create messages in own sessions"
  on public.messages for insert to authenticated
  with check (
    exists (
      select 1 from public.sessions
      where sessions.id = messages.session_id
        and sessions.user_id = (select auth.uid())
    )
  );
