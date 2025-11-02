import os
import json
import re
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()
DB = os.getenv("DATABASE_URL")


def parse_print_run(serial_number: str | None):
    if not serial_number:
        return None
    m = re.search(r"/\s*(\d+)\b", serial_number)
    return int(m.group(1)) if m else None


def build_title(i: dict) -> str:
    parts = [
        str(i["year"]) if i.get("year") else None,
        i.get("set_name"),
        i.get("player"),
        f'#{i["card_number"]}' if i.get("card_number") else None,
        i.get("parallel"),
        (
            f'{i["grade_company"]} {i["grade_value"]}'
            if i.get("grade_company") and i.get("grade_value")
            else None
        ),
    ]
    return " ".join([p for p in parts if p])


def ebay_aspects(i: dict) -> dict:
    aspects = {}

    def add(name, val):
        if val is None or val == "":
            return
        # eBay aspects use arrays of strings
        aspects[name] = [str(val)]

    add("Year Manufactured", i.get("year"))
    add("Set", i.get("set_name"))
    if i.get("subset"):
        add("Subset", i["subset"])
    add("Card Number", i.get("card_number"))
    add("Player/Athlete", i.get("player"))
    if i.get("parallel"):
        add("Parallel/Variety", i["parallel"])
    if i.get("serial_number"):
        add("Serial Numbered", "Yes")
        pr = parse_print_run(i.get("serial_number"))
        if pr:
            add("Print Run", pr)
    add("Sport", i.get("sport"))
    if i.get("grade_company"):
        add("Professional Grader", i["grade_company"])
    if i.get("grade_value"):
        add("Grade", i["grade_value"])
    if i.get("grade_cert"):
        add("Certification Number", i["grade_cert"])
    # Common flags you can toggle later:
    # aspects["Autographed"] = ["Yes"] / ["No"]
    # aspects["Game-Used"] = ["Yes"] / ["No"]
    return aspects


def ebay_listing_skeleton(i: dict) -> dict:
    return {
        "sku": i["sku"],
        "title": build_title(i),
        "condition": "Used",  # collectibles default
        "price": None,  # set during listing
        "quantity": 1,
        # eBay Sell Inventory/Listing flows expect category_id and aspects;
        # you will set category_id during actual listing create.
        "aspects": ebay_aspects(i),
        "description": i.get("notes") or "",
        # images: supply later from photos table after upload to object storage
    }


def amazon_attributes_draft(i: dict) -> dict:
    """
    Draft payload shaped for SP-API Listings Items.
    Final required fields depend on productType schema.
    Replace productType with the exact type when you fetch PTD.
    """
    title = build_title(i)
    attrs = {
        "item_name": [{"value": title}],
        "brand": [{"value": i.get("set_name") or "Unbranded"}],
        "manufacturer": [{"value": i.get("set_name") or "Unknown"}],
        "item_sku": [{"value": i["sku"]}],
        # Card-specific custom block you will remap once you load the official schema
        "card_player": [{"value": i.get("player") or ""}],
        "card_set": [{"value": i.get("set_name") or ""}],
        "card_number": [{"value": i.get("card_number") or ""}],
        "card_parallel": [{"value": i.get("parallel") or ""}],
        "card_year": [{"value": str(i.get("year")) if i.get("year") else ""}],
        "card_serial_number": [{"value": i.get("serial_number") or ""}],
        "card_sport": [{"value": i.get("sport") or ""}],
        "graded": [{"value": "Yes" if i.get("grade_company") else "No"}],
        "grader": [{"value": i.get("grade_company") or ""}],
        "grade": [{"value": i.get("grade_value") or ""}],
        "grade_cert": [{"value": i.get("grade_cert") or ""}],
    }
    return {"productType": "trading_card_draft", "attributes": attrs}  # placeholder


def fetch_item(conn, sku: str) -> dict:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("select * from items where sku=%s", (sku,))
        row = cur.fetchone()
        if not row:
            raise SystemExit(f"SKU not found: {sku}")
        return row


def main():
    import argparse
    import pathlib

    ap = argparse.ArgumentParser()
    ap.add_argument("--sku", required=True)
    args = ap.parse_args()

    outdir = pathlib.Path("out")
    outdir.mkdir(exist_ok=True)

    with psycopg.connect(DB) as conn:
        i = fetch_item(conn, args.sku)
        ebay_payload = ebay_listing_skeleton(i)
        amzn_payload = amazon_attributes_draft(i)

    epath = outdir / f"ebay_{args.sku}.json"
    apath = outdir / f"amazon_{args.sku}.json"
    epath.write_text(json.dumps(ebay_payload, indent=2))
    apath.write_text(json.dumps(amzn_payload, indent=2))
    print(f"Wrote {epath}")
    print(f"Wrote {apath}")


if __name__ == "__main__":
    main()
