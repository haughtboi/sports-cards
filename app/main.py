from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from .db import pool

app = FastAPI(title="Sports Cards Inventory")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class ItemIn(BaseModel):
    sku: str
    title: str
    sport: str | None = None
    year: int | None = None
    set_name: str | None = None
    subset: str | None = None
    card_number: str | None = None
    player: str | None = None
    parallel: str | None = None
    serial_number: str | None = None
    condition: str | None = None
    grade_company: str | None = None
    grade_value: str | None = None
    grade_cert: str | None = None
    acquisition_cost: float | None = 0
    acquired_at: str | None = None
    supplier: str | None = None
    location_bin: str
    notes: str | None = None


def fetch_items():
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select id, sku, title, sport, year, set_name, card_number, player, parallel, location_bin
            from items order by created_at desc limit 200
        """
        )
        cols = [c.name for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def insert_item(i: ItemIn):
    with pool.connection() as conn, conn.cursor() as cur:
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
              sport=excluded.sport,
              year=excluded.year,
              set_name=excluded.set_name,
              subset=excluded.subset,
              card_number=excluded.card_number,
              player=excluded.player,
              parallel=excluded.parallel,
              serial_number=excluded.serial_number,
              condition=excluded.condition,
              grade_company=excluded.grade_company,
              grade_value=excluded.grade_value,
              grade_cert=excluded.grade_cert,
              acquisition_cost=excluded.acquisition_cost,
              acquired_at=excluded.acquired_at,
              supplier=excluded.supplier,
              location_bin=excluded.location_bin,
              notes=excluded.notes,
              updated_at=now()
        """,
            i.model_dump(),
        )
        conn.commit()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "items_list.html", {"request": request, "items": fetch_items()}
    )


@app.get("/new", response_class=HTMLResponse)
def new_item(request: Request):
    return templates.TemplateResponse("item_form.html", {"request": request})


@app.post("/create")
def create_item(
    sku: str = Form(...),
    title: str = Form(...),
    sport: str | None = Form(None),
    year: int | None = Form(None),
    set_name: str | None = Form(None),
    subset: str | None = Form(None),
    card_number: str | None = Form(None),
    player: str | None = Form(None),
    parallel: str | None = Form(None),
    serial_number: str | None = Form(None),
    condition: str | None = Form(None),
    grade_company: str | None = Form(None),
    grade_value: str | None = Form(None),
    grade_cert: str | None = Form(None),
    acquisition_cost: float | None = Form(0),
    acquired_at: str | None = Form(None),
    supplier: str | None = Form(None),
    location_bin: str = Form(...),
    notes: str | None = Form(None),
):
    i = ItemIn(**locals())
    insert_item(i)
    return RedirectResponse("/", status_code=303)
