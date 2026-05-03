from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from database.db import get_db
from functools import wraps

cart_bp = Blueprint('cart', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Login required', 'login_required': True}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@cart_bp.route('/cart')
@login_required
def cart_page():
    return render_template('cart.html')

@cart_bp.route('/api/cart', methods=['GET'])
@login_required
def get_cart():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id, c.quantity, c.product_id,
               p.name, p.price, p.image, p.category
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (user_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    total = sum(item['price'] * item['quantity'] for item in items)
    return jsonify({'items': items, 'total': float(total), 'count': len(items)})

@cart_bp.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    user_id = session['user_id']
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'error': 'product_id is required'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Check product exists
    cursor.execute("SELECT id, name FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

    try:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (user_id, product_id, quantity, quantity))
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': f"{product['name']} added to cart"})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/api/cart/update', methods=['PUT'])
@login_required
def update_cart():
    user_id = session['user_id']
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if quantity < 1:
        return remove_from_cart_helper(user_id, product_id)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
        (quantity, user_id, product_id)
    )
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@cart_bp.route('/api/cart/remove', methods=['DELETE'])
@login_required
def remove_from_cart():
    user_id = session['user_id']
    data = request.get_json()
    product_id = data.get('product_id')
    return remove_from_cart_helper(user_id, product_id)

def remove_from_cart_helper(user_id, product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Item removed from cart'})

@cart_bp.route('/api/cart/clear', methods=['DELETE'])
@login_required
def clear_cart():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    cursor.close()
    conn.close()
    return jsonify({'success': True})
