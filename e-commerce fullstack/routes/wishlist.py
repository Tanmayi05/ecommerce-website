from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from database.db import get_db
from functools import wraps

wishlist_bp = Blueprint('wishlist', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Login required', 'login_required': True}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@wishlist_bp.route('/wishlist')
@login_required
def wishlist_page():
    return render_template('wishlist.html')

@wishlist_bp.route('/api/wishlist', methods=['GET'])
@login_required
def get_wishlist():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT w.id, w.product_id, p.name, p.price, p.image, p.category
        FROM wishlist w JOIN products p ON w.product_id = p.id
        WHERE w.user_id = %s
    """, (user_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(items)

@wishlist_bp.route('/api/wishlist/add', methods=['POST'])
@login_required
def add_to_wishlist():
    user_id = session['user_id']
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'error': 'product_id is required'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

    try:
        cursor.execute(
            "INSERT IGNORE INTO wishlist (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id)
        )
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': f"{product['name']} added to wishlist"})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/api/wishlist/remove', methods=['DELETE'])
@login_required
def remove_from_wishlist():
    user_id = session['user_id']
    data = request.get_json()
    product_id = data.get('product_id')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM wishlist WHERE user_id = %s AND product_id = %s",
        (user_id, product_id)
    )
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@wishlist_bp.route('/api/wishlist/ids', methods=['GET'])
@login_required
def get_wishlist_ids():
    """Returns just the product IDs in the wishlist — for fast UI checking."""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM wishlist WHERE user_id = %s", (user_id,))
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(ids)
