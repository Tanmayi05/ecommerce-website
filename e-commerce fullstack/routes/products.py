from flask import Blueprint, request, jsonify, render_template, session
from database.db import get_db

products_bp = Blueprint('products', __name__)

@products_bp.route('/categories')
def categories():
    return render_template('categories.html')

@products_bp.route('/api/products')
def get_products():
    category = request.args.get('category', '')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute("SELECT * FROM products WHERE category = %s ORDER BY id", (category,))
    else:
        cursor.execute("SELECT * FROM products ORDER BY category, id")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

@products_bp.route('/api/products/<int:product_id>')
def get_product(product_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product)

@products_bp.route('/api/search')
def search_products():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    # Split query into individual words; filter out empty strings
    keywords = [w for w in q.split() if w]

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Build a WHERE clause: every keyword must match at least one column
    # Uses LOWER() on both sides for true case-insensitive matching
    conditions = []
    params = []
    for word in keywords:
        like = f"%{word.lower()}%"
        conditions.append(
            "(LOWER(name) LIKE %s OR LOWER(category) LIKE %s OR LOWER(description) LIKE %s)"
        )
        params.extend([like, like, like])

    where_clause = " AND ".join(conditions)

    # Priority: products whose name starts with the full query float to top
    priority_like = f"{q.lower()}%"
    params.append(priority_like)

    sql = f"""
        SELECT * FROM products
        WHERE {where_clause}
        ORDER BY
            CASE WHEN LOWER(name) LIKE %s THEN 0 ELSE 1 END,
            name
        LIMIT 60
    """
    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@products_bp.route('/api/categories')
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(categories)
