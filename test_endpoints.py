import urllib.request
import json

base = 'http://127.0.0.1:8000'

def test_get(url):
    req = urllib.request.urlopen(base + url)
    print(f"GET {url}: status {req.status}")
    assert req.status == 200
    return req.read().decode('utf-8')

print("1. Testing web pages...")
test_get('/dashboard')
test_get('/billing')
test_get('/menu')
test_get('/history')
test_get('/reports')

print("\n2. Testing Menu API...")
res = test_get('/api/menu')
menu_data = json.loads(res)
print(f"Menu items fetched: {len(menu_data['items'])}")
assert len(menu_data['items']) >= 20

first_item = menu_data['items'][0]
print(f"First item: {first_item['name']}, Price: ₹{first_item['price']}")

print("\n3. Testing Bill Creation & Decimal Recalculation...")
# Item 1 price * 2, minus ₹10 discount + 5% GST
unit_price = float(first_item['price'])
qty = 2
expected_subtotal = unit_price * qty
expected_taxable = expected_subtotal - 10.0
expected_gst = round(expected_taxable * 0.05, 2)
expected_grand_total = round(expected_taxable + expected_gst, 2)

bill_payload = json.dumps({
    'customer_name': 'Test Student',
    'customer_phone': '9876543210',
    'items': [{'id': first_item['id'], 'quantity': qty}],
    'gst_rate': 5.0,
    'discount_amount': 10.0,
    'payment_method': 'UPI'
}).encode('utf-8')

req = urllib.request.Request(base + '/api/bills', data=bill_payload, headers={'Content-Type': 'application/json'}, method='POST')
resp = urllib.request.urlopen(req)
created_bill = json.loads(resp.read().decode('utf-8'))
bill = created_bill['bill']

print(f"Generated Invoice: {bill['invoice_number']}")
print(f"Subtotal: ₹{bill['subtotal']} (Expected: ₹{expected_subtotal})")
print(f"GST Amount: ₹{bill['gst_amount']} (Expected: ₹{expected_gst})")
print(f"Grand Total: ₹{bill['grand_total']} (Expected: ₹{expected_grand_total})")

assert bill['subtotal'] == expected_subtotal
assert bill['grand_total'] == expected_grand_total

print("\n4. Testing Receipt View...")
test_get(f"/receipt/{bill['id']}")

print("\n5. Testing Add, Toggle & Delete Menu Item...")
add_payload = json.dumps({
    'name': 'Paneer Tikka Roll Special',
    'category': 'Snacks',
    'price': 125.0,
    'is_available': True,
    'description': 'Grilled spiced paneer cubes wrapped with mint chutney'
}).encode('utf-8')

req_add = urllib.request.Request(base + '/api/menu', data=add_payload, headers={'Content-Type': 'application/json'}, method='POST')
resp_add = urllib.request.urlopen(req_add)
new_item = json.loads(resp_add.read().decode('utf-8'))['item']
print(f"Added item ID: {new_item['id']}, Name: {new_item['name']}")

# Toggle item
req_toggle = urllib.request.Request(base + f"/api/menu/{new_item['id']}/toggle", data=b'', headers={}, method='PATCH')
resp_toggle = urllib.request.urlopen(req_toggle)
toggle_res = json.loads(resp_toggle.read().decode('utf-8'))
print(f"Toggled availability to: {toggle_res['is_available']}")
assert toggle_res['is_available'] == 0

# Delete item
req_del = urllib.request.Request(base + f"/api/menu/{new_item['id']}", data=b'', headers={}, method='DELETE')
resp_del = urllib.request.urlopen(req_del)
del_res = json.loads(resp_del.read().decode('utf-8'))
print(f"Deleted test item: {del_res['message']}")

print("\n6. Testing Reports Data API...")
test_get('/api/reports/data?period=today')
test_get('/api/reports/data?period=week')

print("\n==========================================")
print(" ALL 6 TEST SUITES PASSED FLAWLESSLY! ")
print("==========================================")
