-- Run in the Supabase SQL editor before ingesting monitoring events.
create extension if not exists vector;
create extension if not exists pgcrypto;

create table if not exists public.monitoring_embeddings (
    id uuid primary key default gen_random_uuid(),
    event_id text unique not null,
    machine_id text not null,
    event_type text not null,
    severity text,
    content text not null,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(384) not null,
    created_at timestamptz not null default now()
);

create index if not exists monitoring_embeddings_machine_id_idx
    on public.monitoring_embeddings (machine_id);
create index if not exists monitoring_embeddings_event_type_idx
    on public.monitoring_embeddings (event_type);
create index if not exists monitoring_embeddings_embedding_hnsw_idx
    on public.monitoring_embeddings using hnsw (embedding vector_cosine_ops);

create or replace function public.match_monitoring_events(
    query_embedding vector(384),
    match_count integer default 5,
    filter_machine_id text default null,
    filter_severity text default null
)
returns table (
    event_id text, machine_id text, event_type text, severity text,
    content text, metadata jsonb, similarity double precision
)
language sql stable
as $$
    select e.event_id, e.machine_id, e.event_type, e.severity, e.content, e.metadata,
           1 - (e.embedding <=> query_embedding) as similarity
    from public.monitoring_embeddings e
    where (filter_machine_id is null or e.machine_id = filter_machine_id)
      and (filter_severity is null or e.severity = filter_severity)
    order by e.embedding <=> query_embedding
    limit least(greatest(match_count, 1), 20);
$$;

-- The API uses a service-role client. Grant explicit RPC access if using another role.
