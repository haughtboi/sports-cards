import os
import datetime
from dotenv import load_dotenv
import psycopg

load_dotenv()
conn = psycopg.connect(os.getenv("DATABASE_URL"))
conn.execute("set timezone to 'UTC';")

sku = "SC-2019-PRIZM-248-Silver-RAW-000001"
item = dict(
    sku=sku,
    title="2019 Panini Prizm Zion Williamson #248 Silver",
    sport="Basketball",
    year=2019,
    set_name="Panini Prizm",
    subset=None,
    card_number="248",
    player="Zion Williamson",
    parallel="Silver",
    serial_number=None,
    condition="RAW",
    grade_company=None,
    grade_value=None,
    grade_cert=None,
    acquisition_cost=95.00,
    acquired_at=datetime.datetime(2024, 12, 1, tzinfo=datetime.timezone.utc),
    supplier="Local show",
    location_bin="BIN-A1",
    notes="Clean surface. Slight corner softening.",
)

with conn.cursor() as cur:
    cur.execute(
        """
    insert into items
      (sku,title,sport,year,set_name,subset,card_number,player,parallel,serial_number,
       condition,grade_company,grade_value,grade_cert,acquisition_cost,acquired_at,
       supplier,location_bin,notes)
    values
      (%(sku)s,%(title)s,%(sport)s,%(year)s,%(set_name)s,%(subset)s,%(card_number)s,%(player)s,%(parallel)s,%(serial_number)s,
       %(condition)s,%(grade_company)s,%(grade_value)s,%(grade_cert)s,%(acquisition_cost)s,%(acquired_at)s,
       %(supplier)s,%(location_bin)s,%(notes)s)
    on conflict (sku) do update set
      title=excluded.title,
      updated_at=now()
    returning id;
    """,
        item,
    )
    row_id = cur.fetchone()[0]
    conn.commit()
    print(f"Seeded {sku} with id={row_id}")
conn.close()
