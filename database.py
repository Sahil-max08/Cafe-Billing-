import sqlite3
import os
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP

DB_NAME = "cafeteria.db"

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_NAME)

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1,
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_name TEXT DEFAULT 'Walk-in Customer',
            customer_phone TEXT DEFAULT '',
            subtotal REAL NOT NULL,
            gst_rate REAL NOT NULL DEFAULT 5.0,
            gst_amount REAL NOT NULL,
            discount_amount REAL NOT NULL DEFAULT 0.0,
            grand_total REAL NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            menu_item_id INTEGER,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bill_id) REFERENCES bills (id) ON DELETE CASCADE,
            FOREIGN KEY (menu_item_id) REFERENCES menu_items (id) ON DELETE SET NULL
        )
    """)

    conn.commit()

    # Seed menu items if empty
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_sample_menu(cursor)
        conn.commit()
        # Also seed realistic initial bills so reports and dashboard display live data
        seed_sample_bills(cursor)
        conn.commit()

    conn.close()

def seed_sample_menu(cursor):
    sample_items = [
        # Snacks
        ("Samosa (2 pcs with Chutney)", "Snacks", 30.00, 1, "Crispy golden pastry stuffed with spiced potato & peas"),
        ("Pav Bhaji", "Snacks", 90.00, 1, "Spiced mashed vegetable curry served with toasted butter pav"),
        ("Veg Cutlet", "Snacks", 45.00, 1, "Crispy shallow fried breaded vegetable patties"),
        ("Paneer Kathi Roll", "Snacks", 110.00, 1, "Flaky paratha rolled with marinated paneer & bell peppers"),
        ("Peri-Peri French Fries", "Snacks", 70.00, 1, "Hot crispy fries dusted with spicy peri-peri seasoning"),
        ("Cheese Garlic Toast", "Snacks", 80.00, 1, "Crusty baguette with garlic herb butter & melted mozzarella"),
        ("Vada Pav (2 pcs)", "Snacks", 40.00, 1, "Mumbai style spicy potato fritters in soft pav with garlic chutney"),

        # Meals
        ("Masala Dosa", "Meals", 85.00, 1, "Crispy rice crepe filled with potato masala, sambar & chutneys"),
        ("Veg Biryani Combo", "Meals", 140.00, 1, "Aromatic basmati rice cooked with garden vegetables, served with raita"),
        ("Chole Bhature", "Meals", 120.00, 1, "Puffy fried bhature served with rich Amritsari chole & pickled onions"),
        ("Rajma Chawal Bowl", "Meals", 95.00, 1, "Home-style spiced kidney beans served over steamed basmati rice"),
        ("Paneer Butter Masala Combo", "Meals", 160.00, 1, "Rich cottage cheese gravy with 2 butter naans and salad"),
        ("South Indian Mini Thali", "Meals", 130.00, 1, "Rice, Sambar, Rasam, Poriyal, Curd, Appalam & Sweet"),
        ("Veg Fried Rice & Manchurian", "Meals", 150.00, 1, "Wok tossed Indo-Chinese fried rice with crispy veg Manchurian balls"),

        # Beverages
        ("Masala Kulhad Chai", "Beverages", 20.00, 1, "Slow brewed aromatic ginger-cardamom tea in clay cup"),
        ("South Indian Filter Coffee", "Beverages", 30.00, 1, "Strong chicory coffee frothed with creamy boiled milk"),
        ("Cold Coffee with Ice Cream", "Beverages", 75.00, 1, "Thick blended cold coffee crowned with a vanilla scoop"),
        ("Fresh Lime Soda (Sweet/Salt)", "Beverages", 40.00, 1, "Fizzy club soda with freshly squeezed lime and mint"),
        ("Mango Lassi", "Beverages", 60.00, 1, "Creamy sweet yogurt drink infused with Alphonso mango pulp"),
        ("Iced Peach Tea", "Beverages", 65.00, 1, "Refreshing cold brewed black tea with juicy peach notes"),

        # Desserts
        ("Gulab Jamun (2 pcs)", "Desserts", 40.00, 1, "Warm soft milk dumplings soaked in cardamom rose syrup"),
        ("Sizzling Brownie with Fudge", "Desserts", 95.00, 1, "Warm chocolate brownie topped with chocolate fudge sauce"),
        ("Rasgulla (2 pcs)", "Desserts", 45.00, 1, "Spongy cottage cheese balls soaked in light sugar syrup"),
        ("Kulfi Falooda", "Desserts", 70.00, 1, "Traditional malai kulfi served with falooda sev, rose syrup & nuts")
    ]

    cursor.executemany("""
        INSERT INTO menu_items (name, category, price, is_available, description)
        VALUES (?, ?, ?, ?, ?)
    """, sample_items)

def seed_sample_bills(cursor):
    """Seed realistic past bills for the demonstration so graphs and metrics have rich data."""
    now = datetime.now()
    dates = [
        now - timedelta(days=2),
        now - timedelta(days=1),
        now - timedelta(hours=4),
        now - timedelta(hours=2),
        now - timedelta(minutes=45),
    ]

    bills_to_create = [
        {
            "customer": "Aarav Sharma",
            "phone": "9876543210",
            "time": dates[0].strftime("%Y-%m-%d 11:30:00"),
            "payment": "UPI",
            "items": [
                ("Chole Bhature", "Meals", 120.00, 2),
                ("Masala Kulhad Chai", "Beverages", 20.00, 2)
            ],
            "discount": 0.0
        },
        {
            "customer": "Priya Nair",
            "phone": "9823456789",
            "time": dates[1].strftime("%Y-%m-%d 14:15:00"),
            "payment": "Card",
            "items": [
                ("Veg Biryani Combo", "Meals", 140.00, 1),
                ("Gulab Jamun (2 pcs)", "Desserts", 40.00, 1),
                ("Cold Coffee with Ice Cream", "Beverages", 75.00, 1)
            ],
            "discount": 15.0
        },
        {
            "customer": "Rohan Deshmukh",
            "phone": "9988776655",
            "time": dates[2].strftime("%Y-%m-%d 10:20:00"),
            "payment": "Cash",
            "items": [
                ("Samosa (2 pcs with Chutney)", "Snacks", 30.00, 3),
                ("South Indian Filter Coffee", "Beverages", 30.00, 3)
            ],
            "discount": 0.0
        },
        {
            "customer": "Ananya Sen",
            "phone": "9123456780",
            "time": dates[3].strftime("%Y-%m-%d 13:40:00"),
            "payment": "UPI",
            "items": [
                ("Masala Dosa", "Meals", 85.00, 2),
                ("Mango Lassi", "Beverages", 60.00, 2),
                ("Pav Bhaji", "Snacks", 90.00, 1)
            ],
            "discount": 20.0
        },
        {
            "customer": "Vikram Malhotra",
            "phone": "9765432109",
            "time": dates[4].strftime("%Y-%m-%d 16:10:00"),
            "payment": "UPI",
            "items": [
                ("Paneer Kathi Roll", "Snacks", 110.00, 2),
                ("Peri-Peri French Fries", "Snacks", 70.00, 1),
                ("Sizzling Brownie with Fudge", "Desserts", 95.00, 1)
            ],
            "discount": 0.0
        }
    ]

    for idx, b in enumerate(bills_to_create, 1):
        inv_no = f"BILL-DEMO-{idx:04d}"
        subtotal = Decimal('0.00')
        item_rows = []

        for name, cat, price, qty in b["items"]:
            item_tot = Decimal(str(price)) * Decimal(str(qty))
            subtotal += item_tot
            item_rows.append((name, cat, price, qty, float(item_tot)))

        gst_rate = Decimal('5.0')
        discount = Decimal(str(b["discount"]))
        taxable = subtotal - discount
        if taxable < Decimal('0.00'):
            taxable = Decimal('0.00')
        gst_amt = (taxable * gst_rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (taxable + gst_amt).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        cursor.execute("""
            INSERT INTO bills (
                invoice_number, customer_name, customer_phone, subtotal,
                gst_rate, gst_amount, discount_amount, grand_total, payment_method,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Completed', ?)
        """, (
            inv_no, b["customer"], b["phone"], float(subtotal),
            float(gst_rate), float(gst_amt), float(discount),
            float(grand_total), b["payment"], b["time"]
        ))
        bill_id = cursor.lastrowid

        for name, cat, price, qty, item_tot in item_rows:
            cursor.execute("""
                INSERT INTO bill_items (
                    bill_id, menu_item_id, item_name, category, unit_price, quantity, total_price, created_at
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
            """, (bill_id, name, cat, price, qty, item_tot, b["time"]))

# --- Menu Management Queries ---

def get_menu_items(category=None, search=None, only_available=False):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM menu_items WHERE 1=1"
    params = []

    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard])

    if only_available:
        query += " AND is_available = 1"

    query += " ORDER BY category ASC, name ASC"
    cursor.execute(query, params)
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def get_menu_item_by_id(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_menu_item(name, category, price, is_available=1, description=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO menu_items (name, category, price, is_available, description)
        VALUES (?, ?, ?, ?, ?)
    """, (name.strip(), category.strip(), float(price), int(is_available), description.strip()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_menu_item(item_id, name, category, price, is_available, description=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE menu_items
        SET name = ?, category = ?, price = ?, is_available = ?, description = ?
        WHERE id = ?
    """, (name.strip(), category.strip(), float(price), int(is_available), description.strip(), item_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_menu_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def toggle_menu_item_availability(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT is_available FROM menu_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    new_status = 0 if row["is_available"] == 1 else 1
    cursor.execute("UPDATE menu_items SET is_available = ? WHERE id = ?", (new_status, item_id))
    conn.commit()
    conn.close()
    return new_status

# --- Billing Queries ---

def generate_invoice_number():
    """Generate invoice number format: BILL-YYYYMMDD-XXXX."""
    conn = get_db()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"BILL-{today_str}-"

    cursor.execute("SELECT invoice_number FROM bills WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
    row = cursor.fetchone()
    conn.close()

    if row and row["invoice_number"]:
        try:
            last_seq = int(row["invoice_number"].split("-")[-1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1

    return f"{prefix}{new_seq:04d}"

def create_bill(customer_name, customer_phone, items, gst_rate=5.0, discount_amount=0.0, payment_method="Cash"):
    """
    Validate and save bill with server-side recalculation using Decimal arithmetic.
    items: list of dicts with {'id': int, 'quantity': int}
    """
    if not items or len(items) == 0:
        raise ValueError("Order must contain at least one item.")

    if payment_method not in ["Cash", "UPI", "Card"]:
        raise ValueError("Invalid payment method. Allowed: Cash, UPI, Card.")

    conn = get_db()
    cursor = conn.cursor()

    try:
        subtotal = Decimal('0.00')
        bill_items_to_save = []

        for cart_item in items:
            item_id = int(cart_item.get("id"))
            quantity = int(cart_item.get("quantity", 1))

            if quantity <= 0:
                raise ValueError("Item quantity must be greater than 0.")

            cursor.execute("SELECT id, name, category, price, is_available FROM menu_items WHERE id = ?", (item_id,))
            menu_row = cursor.fetchone()
            if not menu_row:
                raise ValueError(f"Menu item with ID {item_id} not found.")

            if menu_row["is_available"] == 0:
                raise ValueError(f"Item '{menu_row['name']}' is currently out of stock.")

            unit_price = Decimal(str(menu_row["price"])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            item_total = (unit_price * Decimal(str(quantity))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            subtotal += item_total

            bill_items_to_save.append({
                "menu_item_id": menu_row["id"],
                "item_name": menu_row["name"],
                "category": menu_row["category"],
                "unit_price": float(unit_price),
                "quantity": quantity,
                "total_price": float(item_total)
            })

        gst_rate_dec = Decimal(str(max(0.0, float(gst_rate))))
        discount_dec = Decimal(str(max(0.0, float(discount_amount)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if discount_dec > subtotal:
            discount_dec = subtotal

        taxable_amt = subtotal - discount_dec
        gst_amt = (taxable_amt * gst_rate_dec / Decimal('100.0')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        grand_total = (taxable_amt + gst_amt).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        invoice_number = generate_invoice_number()
        cust_name = customer_name.strip() if customer_name and customer_name.strip() else "Walk-in Customer"
        cust_phone = customer_phone.strip() if customer_phone else ""

        cursor.execute("""
            INSERT INTO bills (
                invoice_number, customer_name, customer_phone,
                subtotal, gst_rate, gst_amount, discount_amount,
                grand_total, payment_method, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Completed')
        """, (
            invoice_number, cust_name, cust_phone,
            float(subtotal), float(gst_rate_dec), float(gst_amt), float(discount_dec),
            float(grand_total), payment_method
        ))

        bill_id = cursor.lastrowid

        for b_item in bill_items_to_save:
            cursor.execute("""
                INSERT INTO bill_items (
                    bill_id, menu_item_id, item_name, category, unit_price, quantity, total_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_id, b_item["menu_item_id"], b_item["item_name"],
                b_item["category"], b_item["unit_price"], b_item["quantity"], b_item["total_price"]
            ))

        conn.commit()

        # Fetch the complete saved bill to return
        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        saved_bill = dict(cursor.fetchone())
        saved_bill["items"] = bill_items_to_save
        return saved_bill

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_bill_by_id(bill_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    bill_row = cursor.fetchone()
    if not bill_row:
        conn.close()
        return None

    bill = dict(bill_row)
    cursor.execute("SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
    bill["items"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return bill

def get_bill_by_invoice(invoice_number):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills WHERE invoice_number = ?", (invoice_number,))
    bill_row = cursor.fetchone()
    if not bill_row:
        conn.close()
        return None

    bill = dict(bill_row)
    cursor.execute("SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id ASC", (bill["id"],))
    bill["items"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return bill

def get_recent_bills(limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, (SELECT COUNT(*) FROM bill_items bi WHERE bi.bill_id = b.id) as item_count
        FROM bills b
        ORDER BY b.id DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_bills(search=None, start_date=None, end_date=None, payment_method=None, limit=200):
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT b.*, (SELECT COUNT(*) FROM bill_items bi WHERE bi.bill_id = b.id) as item_count
        FROM bills b
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (b.invoice_number LIKE ? OR b.customer_name LIKE ? OR b.customer_phone LIKE ?)"
        wildcard = f"%{search.strip()}%"
        params.extend([wildcard, wildcard, wildcard])

    if payment_method and payment_method.lower() != 'all':
        query += " AND b.payment_method = ?"
        params.append(payment_method)

    if start_date:
        query += " AND date(b.created_at) >= date(?)"
        params.append(start_date)

    if end_date:
        query += " AND date(b.created_at) <= date(?)"
        params.append(end_date)

    query += " ORDER BY b.id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# --- Dashboard & Reports Queries ---

def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")

    # Today sales & orders
    cursor.execute("""
        SELECT COALESCE(SUM(grand_total), 0) as today_sales,
               COUNT(id) as today_orders
        FROM bills
        WHERE date(created_at) = date(?)
    """, (today_str,))
    today_data = cursor.fetchone()

    # Total menu items
    cursor.execute("SELECT COUNT(*) as total_items, SUM(is_available) as available_items FROM menu_items")
    menu_data = cursor.fetchone()

    # Total completed transactions all-time
    cursor.execute("SELECT COUNT(*) as total_completed, COALESCE(SUM(grand_total), 0) as total_revenue FROM bills")
    all_time = cursor.fetchone()

    # Recent bills
    cursor.execute("""
        SELECT b.*, (SELECT COUNT(*) FROM bill_items bi WHERE bi.bill_id = b.id) as item_count
        FROM bills b
        ORDER BY b.id DESC
        LIMIT 6
    """)
    recent_bills = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "today_sales": float(today_data["today_sales"]),
        "today_orders": int(today_data["today_orders"]),
        "total_items": int(menu_data["total_items"] or 0),
        "available_items": int(menu_data["available_items"] or 0),
        "total_completed": int(all_time["total_completed"] or 0),
        "total_revenue": float(all_time["total_revenue"] or 0),
        "recent_bills": recent_bills
    }

def get_sales_reports(period='today', custom_start=None, custom_end=None):
    conn = get_db()
    cursor = conn.cursor()
    today = date.today()

    if period == 'today':
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif period == 'week':
        start_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif period == 'month':
        start_date = (today - timedelta(days=29)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif period == 'all':
        start_date = None
        end_date = None
    elif period == 'custom' and custom_start and custom_end:
        start_date = custom_start
        end_date = custom_end
    else:
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

    date_filter = ""
    params = []
    if start_date and end_date:
        date_filter = "WHERE date(created_at) >= date(?) AND date(created_at) <= date(?)"
        params = [start_date, end_date]

    # Aggregate metrics
    cursor.execute(f"""
        SELECT COUNT(id) as total_orders,
               COALESCE(SUM(grand_total), 0) as total_revenue,
               COALESCE(SUM(subtotal), 0) as total_subtotal,
               COALESCE(SUM(gst_amount), 0) as total_gst,
               COALESCE(SUM(discount_amount), 0) as total_discount,
               COALESCE(AVG(grand_total), 0) as avg_order_value
        FROM bills
        {date_filter}
    """, params)
    summary_row = cursor.fetchone()

    # Top selling items
    top_items_query = f"""
        SELECT bi.item_name, bi.category,
               SUM(bi.quantity) as total_quantity,
               SUM(bi.total_price) as total_sales
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        {date_filter.replace('created_at', 'b.created_at')}
        GROUP BY bi.item_name
        ORDER BY total_quantity DESC
        LIMIT 10
    """
    cursor.execute(top_items_query, params)
    top_items = [dict(r) for r in cursor.fetchall()]

    # Sales by category
    category_query = f"""
        SELECT bi.category,
               SUM(bi.quantity) as total_units,
               SUM(bi.total_price) as category_sales
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        {date_filter.replace('created_at', 'b.created_at')}
        GROUP BY bi.category
        ORDER BY category_sales DESC
    """
    cursor.execute(category_query, params)
    category_sales = [dict(r) for r in cursor.fetchall()]

    # Payment methods breakdown
    payment_query = f"""
        SELECT payment_method,
               COUNT(id) as count,
               SUM(grand_total) as total_amount
        FROM bills
        {date_filter}
        GROUP BY payment_method
    """
    cursor.execute(payment_query, params)
    payment_methods = [dict(r) for r in cursor.fetchall()]

    # Daily trend (for charts)
    trend_query = f"""
        SELECT date(created_at) as sale_date,
               COUNT(id) as order_count,
               SUM(grand_total) as daily_revenue
        FROM bills
        {date_filter}
        GROUP BY date(created_at)
        ORDER BY date(created_at) ASC
    """
    cursor.execute(trend_query, params)
    daily_trends = [dict(r) for r in cursor.fetchall()]

    # List of bills during this period
    cursor.execute(f"""
        SELECT b.*, (SELECT COUNT(*) FROM bill_items bi WHERE bi.bill_id = b.id) as item_count
        FROM bills b
        {date_filter}
        ORDER BY b.id DESC
    """, params)
    period_bills = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "total_orders": int(summary_row["total_orders"]),
        "total_revenue": float(summary_row["total_revenue"]),
        "total_subtotal": float(summary_row["total_subtotal"]),
        "total_gst": float(summary_row["total_gst"]),
        "total_discount": float(summary_row["total_discount"]),
        "avg_order_value": float(summary_row["avg_order_value"]),
        "top_items": top_items,
        "category_sales": category_sales,
        "payment_methods": payment_methods,
        "daily_trends": daily_trends,
        "period_bills": period_bills
    }
