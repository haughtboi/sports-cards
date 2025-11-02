-- reference
create extension if not exists pgcrypto;

create table if not exists price_sources(
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null
);

create table if not exists marketplaces(
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  seller_id text,
  auth jsonb
);

-- inventory
create table if not exists items(
  id uuid primary key default gen_random_uuid(),
  sku text unique not null,
  title text not null,
  sport text, year int, set_name text, subset text,
  card_number text, player text,
  parallel text, serial_number text,
  condition text,
  grade_company text, grade_value text, grade_cert text,
  acquisition_cost numeric(12,2) default 0,
  acquired_at timestamptz, supplier text,
  location_bin text not null,
  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create index if not exists items_player_idx on items(player);
create index if not exists items_ycs_idx on items(year,set_name,card_number);
create index if not exists items_loc_idx on items(location_bin);

create table if not exists photos(
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id) on delete cascade,
  uri text not null,
  kind text,
  created_at timestamptz default now()
);

create table if not exists listings(
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id) on delete cascade,
  marketplace_id uuid references marketplaces(id) on delete cascade,
  remote_listing_id text,
  status text not null,
  price numeric(12,2),
  quantity int default 1,
  fees_pct numeric(5,2),
  shipping_profile text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(item_id, marketplace_id)
);
create index if not exists listings_status_idx on listings(status);

create table if not exists prices(
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id) on delete cascade,
  source_id uuid references price_sources(id),
  price numeric(12,2) not null,
  currency text default 'USD',
  kind text not null,                     -- 'SOLD','ASK','MODEL'
  observed_at timestamptz not null,
  payload jsonb
);
create index if not exists prices_item_time_idx on prices(item_id, observed_at desc);

create table if not exists sales(
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id),
  marketplace_id uuid references marketplaces(id),
  order_id text,
  sale_price numeric(12,2) not null,
  shipping_income numeric(12,2) default 0,
  fees numeric(12,2) default 0,
  tax numeric(12,2) default 0,
  sold_at timestamptz not null,
  buyer_location text
);
create index if not exists sales_sold_time_idx on sales(sold_at desc);
