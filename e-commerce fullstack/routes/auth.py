from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
import bcrypt
from database.db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('auth.index'))
        return render_template('login.html')

    # POST — handle AJAX or form login
    data = request.get_json() or request.form
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({'success': False, 'message': 'No account found with that email'}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'success': False, 'message': 'Incorrect password'}), 401

    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['is_admin'] = user['is_admin']

    return jsonify({
        'success': True,
        'message': f"Welcome back, {user['name']}!",
        'user': {'name': user['name'], 'email': user['email'], 'is_admin': user['is_admin']}
    })

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('login.html', mode='signup')

    data = request.get_json() or request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()

        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['is_admin'] = False

        return jsonify({
            'success': True,
            'message': f"Account created! Welcome, {name}!",
            'user': {'name': name, 'email': email}
        })
    except Exception as e:
        cursor.close()
        conn.close()
        if 'Duplicate entry' in str(e):
            return jsonify({'success': False, 'message': 'An account with this email already exists'}), 409
        return jsonify({'success': False, 'message': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/api/me')
def me():
    if 'user_id' not in session:
        return jsonify({'logged_in': False})
    return jsonify({
        'logged_in': True,
        'user': {
            'id': session['user_id'],
            'name': session['user_name'],
            'email': session['user_email'],
            'is_admin': session.get('is_admin', False)
        }
    })
