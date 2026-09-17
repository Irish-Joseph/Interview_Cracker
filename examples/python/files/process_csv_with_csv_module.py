"""
Topic: Practical CSV processing with the csv module.

Concepts:
- csv.DictReader / DictWriter (row -> dict)
- The csv module's quoting rules (commas and quotes in fields)
- Filtering and aggregating tabular data
- Writing results back out as CSV
- Handling a file that might not have a header

CSV is the most common data interchange format you will meet in
scripts and jobs. The standard library csv module handles the nasty
parts (embedded commas, quotes, newlines) for you.

Example input (orders.csv):
    id,customer,product,amount
    1,Acme,Widget,25.50
    2,"Globex, Inc.",Gadget,19.99
    3,Initech,Widget,12.00

Time Complexity: O(rows)
"""

import csv
import io
from collections import defaultdict

SAMPLE_CSV = """\
id,customer,product,amount
1,Acme,Widget,25.50
2,"Globex, Inc.",Gadget,19.99
3,Initech,Widget,12.00
4,Acme,Gadget,30.00
5,Umbrella,Widget,8.25
"""


def read_rows(text: str) -> list[dict[str, str]]:
    """Parse CSV text into a list of dicts (header -> value)."""
    # io.StringIO lets us use file-accepting csv readers on a string.
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def total_by_product(rows: list[dict[str, str]]) -> dict[str, float]:
    """Sum amount per product."""
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        totals[row["product"]] += float(row["amount"])
    return dict(totals)


def top_customers(rows: list[dict[str, str]], limit: int = 2) -> list[tuple[str, int]]:
    """The `limit` customers with the most orders."""
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["customer"]] += 1
    # Sort by count desc, then name asc for deterministic ties.
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:limit]


def write_csv(rows: list[dict], fieldnames: list[str]) -> str:
    """Serialize rows back to CSV text (for testing / round-trips).

    Only the named fields are written; extra keys in the row dicts
    are dropped (DictWriter raises on unknown keys otherwise).
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows({key: row[key] for key in fieldnames} for row in rows)
    return buffer.getvalue()


# --- Demo -----------------------------------------------------------------

rows = read_rows(SAMPLE_CSV)

# Notice how DictReader correctly handled the quoted field containing
# a comma — 'Globex, Inc.' is ONE customer, not two columns.
print(f"parsed {len(rows)} rows; customers: {sorted({r['customer'] for r in rows})}")

print("\ntotal by product:")
for product, total in sorted(total_by_product(rows).items()):
    print(f"  {product}: {total:.2f}")

print(f"\ntop customers: {top_customers(rows)}")

# Filter + write: export only Acme's orders to a new CSV.
acme_orders = [r for r in rows if r["customer"] == "Acme"]
export = write_csv(acme_orders, ["id", "product", "amount"])
print("\nAcme export:")
print(export, end="")

# Expected tail output:
# id,product,amount
# 1,Widget,25.50
# 4,Gadget,30.00
