# Restaurant Management System — Backend

A Django + Django REST Framework backend for restaurant operations: menu, orders,
tables, reservations, and inventory — with automatic inventory deduction on order
confirmation and low-stock/sales reporting.

## Stack
- Django 6 + Django REST Framework
- django-filter for query filtering
- SQLite by default (swap `DATABASES` in `core/settings.py` for Postgres/MySQL in production)

## Setup
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # for /admin/
python manage.py seed_data         # optional: sample menu, inventory, tables
python manage.py runserver
```
Admin panel: `http://127.0.0.1:8000/admin/`
API root:    `http://127.0.0.1:8000/api/`

## Apps & Models
- **menu** — `Category`, `MenuItem`, `RecipeItem` (how much of each `InventoryItem`
  a dish consumes — this is what powers auto stock deduction)
- **tables** — `Table` (number, capacity, status: available/occupied/reserved/cleaning)
- **reservations** — `Reservation` (validates party size vs. table capacity and
  rejects overlapping time slots for the same table)
- **orders** — `Order`, `OrderItem` (order lifecycle + inventory deduction logic)
- **inventory** — `InventoryItem`, `StockMovement` (full audit trail of every stock change)
- **reports** — daily sales and low-stock alert endpoints

## Key endpoints

| Purpose                         | Endpoint                                                   |
|----------------------------------|-------------------------------------------------------------|
| Menu (list/detail)               | `GET /api/menu-items/`                                      |
| Only sellable items right now    | `GET /api/menu-items/orderable/`                             |
| Categories                       | `GET/POST /api/categories/`                                  |
| Tables                           | `GET/POST /api/tables/`                                      |
| Free tables for a party size     | `GET /api/tables/available/?party_size=4`                    |
| Reservations                     | `GET/POST /api/reservations/`                                 |
| Check a slot before booking      | `GET /api/reservations/check-availability/?table=1&time=2026-09-20T19:00:00Z` |
| Seat / cancel a reservation      | `POST /api/reservations/{id}/seat/`, `.../cancel/`            |
| Place an order                   | `POST /api/orders/` (see payload below)                       |
| Confirm order (deducts stock)    | `POST /api/orders/{id}/confirm/`                              |
| Advance kitchen status           | `POST /api/orders/{id}/advance/` `{"status": "preparing"}`    |
| Complete / pay                   | `POST /api/orders/{id}/complete/`                              |
| Cancel (restocks if confirmed)   | `POST /api/orders/{id}/cancel/`                                |
| Inventory list                   | `GET /api/inventory/`                                          |
| Restock an item                  | `POST /api/inventory/{id}/restock/` `{"amount": 500}`          |
| Low stock items                  | `GET /api/inventory/low-stock/`                                |
| Daily sales report                | `GET /api/reports/daily-sales/?date=2026-09-15`                |
| Stock alerts report               | `GET /api/reports/stock-alerts/`                                |

### Placing an order
```json
POST /api/orders/
{
  "table": 3,
  "order_type": "dine_in",
  "items_input": [
    {"menu_item": 1, "quantity": 2},
    {"menu_item": 3, "quantity": 1, "special_instructions": "no sugar"}
  ]
}
```
This creates the order in `pending` status without touching stock. Call
`POST /api/orders/{id}/confirm/` to validate stock across every line item and
atomically deduct it — the whole confirmation fails (no partial deduction) if
anything is short, and the response explains what's missing.

## Order lifecycle
`pending → confirmed (stock deducted, table → occupied) → preparing → ready →
served → completed (table → cleaning)`, or `cancelled` at any point before
completion (restocks inventory automatically if it had already been deducted).

## Business logic highlights
- **`MenuItem.is_in_stock`** checks every ingredient's live quantity against
  the recipe — an item silently disappears from `/orderable/` the moment an
  ingredient runs out, no manual flag needed.
- **`Order.confirm()`** is wrapped in a DB transaction: it totals ingredient
  needs across *all* lines first (so two lines sharing an ingredient are
  checked correctly), then deducts — all or nothing.
- **`Reservation`** validation rejects a booking if the party is too big for
  the table or if it overlaps another confirmed/seated reservation on the
  same table.
- Every stock change (restock, order deduction, cancellation refund) is
  logged to `StockMovement` for a full audit trail.

## Tests
A smoke test covering the full order → inventory → table → cancel flow was
run against this codebase during development (seed data, confirm order,
verify deductions, cancel, verify restock, reject an under-stocked order).
Add these as proper `pytest`/`TestCase` cases under each app's `tests.py`
for CI.



<img width="1516" height="817" alt="Screenshot 2026-09-19 113315" src="https://github.com/user-attachments/assets/0d52a039-3962-4262-8211-80119984c5cc" />
