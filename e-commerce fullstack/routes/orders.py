from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from database.db import get_db
from functools import wraps

orders_bp = Blueprint('orders', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Login required', 'login_required': True}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@orders_bp.route('/payment')
@login_required
def payment_page():
    return render_template('payment.html')

@orders_bp.route('/orders')
@login_required
def orders_page():
    return render_template('orders.html')

@orders_bp.route('/api/orders/place', methods=['POST'])
@login_required
def place_order():
    user_id = session['user_id']
    data = request.get_json()
    payment_method = data.get('payment_method', 'cod')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Fetch cart items
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.name, p.price
        FROM cart c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Cart is empty'}), 400

    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    try:
        # Create order
        cursor.execute(
            "INSERT INTO orders (user_id, total_price, payment_method, status) VALUES (%s, %s, %s, 'confirmed')",
            (user_id, total_price, payment_method)
        )
        order_id = cursor.lastrowid

        # Insert order items
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item['product_id'], item['name'], item['quantity'], item['price']))

        # Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

        cursor.close()
        conn.close()
        return jsonify({
            'success': True,
            'order_id': order_id,
            'total': float(total_price),
            'message': 'Order placed successfully!'
        })
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.id, o.total_price, o.status, o.payment_method, o.created_at
        FROM orders o WHERE o.user_id = %s ORDER BY o.created_at DESC
    """, (user_id,))
    orders = cursor.fetchall()

    for order in orders:
        cursor.execute("""
            SELECT product_name, quantity, price
            FROM order_items WHERE order_id = %s
        """, (order['id'],))
        order['items'] = cursor.fetchall()
        order['created_at'] = order['created_at'].strftime('%d %b %Y, %I:%M %p') if order['created_at'] else ''
        order['total_price'] = float(order['total_price'])

    cursor.close()
    conn.close()
    return jsonify(orders)

@orders_bp.route('/api/orders/<int:order_id>/cancel', methods=['PUT'])
@login_required
def cancel_order(order_id):
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = 'cancelled' WHERE id = %s AND user_id = %s AND status = 'pending'",
        (order_id, user_id)
    )
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    if affected:
        return jsonify({'success': True})
    return jsonify({'error': 'Order cannot be cancelled'}), 400
