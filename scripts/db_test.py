import os
from dotenv import load_dotenv
import psycopg

load_dotenv()
conn = psycopg.connect(os.getenv("DATABASE_URL"))
with conn.cursor() as cur:
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
    )
    for (name,) in cur.fetchall():
        print(name)
conn.close()
