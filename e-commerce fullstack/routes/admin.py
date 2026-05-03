from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from database.db import get_db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@admin_bp.route('/products', methods=['POST'])
@admin_required
def add_product():
    data = request.get_json()
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    image = data.get('image', '')
    description = data.get('description', '')

    if not name or not category or not price:
        return jsonify({'error': 'name, category, and price are required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, image, description) VALUES (%s, %s, %s, %s, %s)",
        (name, category, price, image, description)
    )
    product_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'product_id': product_id})

@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    data = request.get_json()
    fields = []
    values = []
    for key in ['name', 'category', 'price', 'image', 'description', 'stock']:
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])
    if not fields:
        return jsonify({'error': 'Nothing to update'}), 400
    values.append(product_id)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = %s", values)
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    users = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as total_products FROM products")
    products = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) as total_orders, COALESCE(SUM(total_price),0) as revenue FROM orders WHERE status != 'cancelled'")
    orders = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({
        'total_users': users['total_users'],
        'total_products': products['total_products'],
        'total_orders': orders['total_orders'],
        'revenue': float(orders['revenue'])
    })

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, o.total_price, o.status, o.payment_method, o.created_at,
               u.name as user_name, u.email as user_email
        FROM orders o JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC LIMIT 100
    """)
    orders = cursor.fetchall()
    for o in orders:
        o['created_at'] = o['created_at'].strftime('%d %b %Y') if o['created_at'] else ''
        o['total_price'] = float(o['total_price'])
    cursor.close()
    conn.close()
    return jsonify(orders)
