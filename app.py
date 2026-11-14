from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from datetime import datetime
import database

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Disable browser caching so the fresh Cafeteria system is always loaded
@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Custom Jinja Template Filters
@app.template_filter('currency')
def currency_filter(value):
    try:
        val = float(value)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"

@app.template_filter('format_datetime')
def format_datetime_filter(value):
    if not value:
        return ""
    try:
        # Handles SQLite 'YYYY-MM-DD HH:MM:SS'
        dt = datetime.strptime(str(value).split('.')[0], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(value)

# Page Routes

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    stats = database.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats, active_page='dashboard')

@app.route('/billing')
def billing():
    menu_items = database.get_menu_items(only_available=True)
    categories = sorted(list(set(item['category'] for item in menu_items)))
    return render_template('billing.html', menu_items=menu_items, categories=categories, active_page='billing')

@app.route('/menu')
def menu_page():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    menu_items = database.get_menu_items(category=category, search=search)
    all_items = database.get_menu_items()
    categories = sorted(list(set(item['category'] for item in all_items)))
    return render_template('menu.html', menu_items=menu_items, categories=categories,
                           current_category=category, search_query=search, active_page='menu')

@app.route('/history')
def history():
    search = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    payment_method = request.args.get('payment_method', 'all')

    bills = database.get_bills(
        search=search if search else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        payment_method=payment_method if payment_method != 'all' else None
    )
    return render_template('history.html', bills=bills, search=search,
                           start_date=start_date, end_date=end_date,
                           payment_method=payment_method, active_page='history')

@app.route('/reports')
def reports():
    period = request.args.get('period', 'today')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    report_data = database.get_sales_reports(
        period=period,
        custom_start=start_date if period == 'custom' else None,
        custom_end=end_date if period == 'custom' else None
    )
    return render_template('reports.html', report=report_data, period=period,
                           start_date=start_date, end_date=end_date, active_page='reports')

@app.route('/receipt/<int:bill_id>')
def view_receipt(bill_id):
    bill = database.get_bill_by_id(bill_id)
    if not bill:
        flash("Receipt not found.", "error")
        return redirect(url_for('history'))
    return render_template('receipt.html', bill=bill, bill_items=bill.get('items', []))

# REST API Endpoints

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    stats = database.get_dashboard_stats()
    return jsonify({"success": True, "data": stats})

@app.route('/api/menu', methods=['GET', 'POST'])
def api_menu():
    if request.method == 'GET':
        category = request.args.get('category')
        search = request.args.get('search')
        only_avail = request.args.get('only_available') == 'true'
        items = database.get_menu_items(category=category, search=search, only_available=only_avail)
        return jsonify({"success": True, "items": items})

    elif request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        price = data.get('price')
        is_available = 1 if data.get('is_available', True) else 0
        description = data.get('description', '').strip()

        if not name:
            return jsonify({"success": False, "error": "Item name is required."}), 400
        if not category:
            return jsonify({"success": False, "error": "Category is required."}), 400

        try:
            price_val = float(price)
            if price_val < 0:
                return jsonify({"success": False, "error": "Price cannot be negative."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid price entered."}), 400

        new_id = database.add_menu_item(name, category, price_val, is_available, description)
        item = database.get_menu_item_by_id(new_id)
        return jsonify({"success": True, "message": "Item added successfully.", "item": item}), 201

@app.route('/api/menu/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def api_menu_item(item_id):
    if request.method == 'GET':
        item = database.get_menu_item_by_id(item_id)
        if not item:
            return jsonify({"success": False, "error": "Item not found."}), 404
        return jsonify({"success": True, "item": item})

    elif request.method == 'PUT':
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        price = data.get('price')
        is_available = 1 if data.get('is_available', True) else 0
        description = data.get('description', '').strip()

        if not name or not category:
            return jsonify({"success": False, "error": "Name and category are required."}), 400

        try:
            price_val = float(price)
            if price_val < 0:
                return jsonify({"success": False, "error": "Price cannot be negative."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid price format."}), 400

        updated = database.update_menu_item(item_id, name, category, price_val, is_available, description)
        if not updated:
            return jsonify({"success": False, "error": "Item not found."}), 404

        item = database.get_menu_item_by_id(item_id)
        return jsonify({"success": True, "message": "Item updated successfully.", "item": item})

    elif request.method == 'DELETE':
        deleted = database.delete_menu_item(item_id)
        if not deleted:
            return jsonify({"success": False, "error": "Item not found or already deleted."}), 404
        return jsonify({"success": True, "message": "Item deleted successfully."})

@app.route('/api/menu/<int:item_id>/toggle', methods=['PATCH'])
def api_toggle_menu_item(item_id):
    new_status = database.toggle_menu_item_availability(item_id)
    if new_status is None:
        return jsonify({"success": False, "error": "Item not found."}), 404
    return jsonify({
        "success": True,
        "is_available": new_status,
        "message": "Item marked as in-stock." if new_status == 1 else "Item marked as out-of-stock."
    })

@app.route('/api/bills', methods=['GET', 'POST'])
def api_bills():
    if request.method == 'GET':
        search = request.args.get('search')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        payment_method = request.args.get('payment_method')
        bills = database.get_bills(search=search, start_date=start_date, end_date=end_date, payment_method=payment_method)
        return jsonify({"success": True, "bills": bills})

    elif request.method == 'POST':
        data = request.get_json() or {}
        customer_name = data.get('customer_name', '').strip()
        customer_phone = data.get('customer_phone', '').strip()
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'Cash')

        try:
            gst_rate = float(data.get('gst_rate', 5.0))
        except (ValueError, TypeError):
            gst_rate = 5.0

        try:
            discount_amount = float(data.get('discount_amount', 0.0))
        except (ValueError, TypeError):
            discount_amount = 0.0

        if not items or not isinstance(items, list):
            return jsonify({"success": False, "error": "Order must contain at least one item."}), 400

        try:
            bill = database.create_bill(
                customer_name=customer_name,
                customer_phone=customer_phone,
                items=items,
                gst_rate=gst_rate,
                discount_amount=discount_amount,
                payment_method=payment_method
            )
            return jsonify({
                "success": True,
                "message": "Bill generated successfully!",
                "bill": bill
            }), 201
        except ValueError as ve:
            return jsonify({"success": False, "error": str(ve)}), 400
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to generate bill: {str(e)}"}), 500

@app.route('/api/bills/<int:bill_id>', methods=['GET'])
def api_get_bill(bill_id):
    bill = database.get_bill_by_id(bill_id)
    if not bill:
        return jsonify({"success": False, "error": "Bill not found."}), 404
    return jsonify({"success": True, "bill": bill})

@app.route('/api/reports/data', methods=['GET'])
def api_reports_data():
    period = request.args.get('period', 'today')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    report_data = database.get_sales_reports(
        period=period,
        custom_start=start_date if period == 'custom' else None,
        custom_end=end_date if period == 'custom' else None
    )
    return jsonify({"success": True, "report": report_data})

if __name__ == '__main__':
    database.init_db()
    print("=" * 60)
    print(" ☕ CAMPUS CAFETERIA BILLING SYSTEM")
    print(" Backend running at: http://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
