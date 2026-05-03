# Flipkart Clone — Full Stack Flask + MySQL

Your existing frontend-only Flipkart clone has been upgraded to a full-stack application with:
- **Flask backend** with REST APIs
- **MySQL database** with proper schema
- **BCrypt authentication** (signup/login/logout)
- **Server-side cart, wishlist, orders**
- **Live search API**
- **Admin dashboard**

---

## 📁 Project Structure

```
flipkart_fullstack/
├── app.py                  ← Flask entry point
├── requirements.txt        ← Python dependencies
├── database/
│   ├── __init__.py
│   ├── db.py               ← MySQL connection + table creation + seeding
│   └── schema.sql          ← Raw SQL schema (optional manual setup)
├── routes/
│   ├── __init__.py
│   ├── auth.py             ← /login, /signup, /logout, /api/me
│   ├── products.py         ← /api/products, /api/search, /api/categories
│   ├── cart.py             ← /api/cart (GET/add/update/remove/clear)
│   ├── orders.py           ← /api/orders/place, /api/orders
│   ├── wishlist.py         ← /api/wishlist (GET/add/remove)
│   └── admin.py            ← /admin/* (protected, admin only)
├── templates/
│   ├── base.html           ← Shared navbar, flash messages, auth state
│   ├── index.html          ← Homepage with featured products
│   ├── login.html          ← Login + Signup tabs
│   ├── categories.html     ← Product grid with filters + search
│   ├── cart.html           ← Cart page
│   ├── payment.html        ← Checkout + order placement
│   ├── wishlist.html       ← Wishlist page
│   ├── orders.html         ← Order history
│   └── admin.html          ← Admin dashboard
└── static/
    ├── css/
    │   ├── styles.css
    │   ├── cart.css
    │   └── categories.css
    └── images/             ← All product images (copied from your original project)
```

---

## ⚙️ Setup Instructions

### Step 1 — Install MySQL
Make sure MySQL is running on your machine. Then create the database:

```bash
mysql -u root -p
```
```sql
CREATE DATABASE flipkart_db;
EXIT;
```

### Step 2 — Configure Database Credentials

Edit `database/db.py` and update:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',   # ← change this
    'database': 'flipkart_db',
}
```

Or set environment variables (recommended for production):
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_NAME=flipkart_db
export SECRET_KEY=some-random-secret-key
```

### Step 3 — Install Python Dependencies

```bash
cd flipkart_fullstack
pip install -r requirements.txt
```

Required packages:
| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `flask-session` | Server-side sessions |
| `mysql-connector-python` | MySQL connection |
| `bcrypt` | Password hashing |

### Step 4 — Run the Application

```bash
python app.py
```

Open your browser: **http://localhost:5000**

> On first run, Flask auto-creates all tables and seeds 43 products from your existing images!

---

## 🔐 Creating an Admin User

After running the app once (so tables are created), connect to MySQL:

```sql
USE flipkart_db;
-- First sign up normally at http://localhost:5000/signup
-- Then promote that user to admin:
UPDATE users SET is_admin = TRUE WHERE email = 'your@email.com';
```

Then visit **http://localhost:5000/admin** while logged in.

---

## 🌐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET/POST | `/login` | Login |
| GET/POST | `/signup` | Register |
| GET | `/logout` | Logout |
| GET | `/api/me` | Get current user info |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | All products (optionally `?category=X`) |
| GET | `/api/products/<id>` | Single product |
| GET | `/api/search?q=keyword` | Search products |
| GET | `/api/categories` | List all categories |

### Cart (requires login)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cart` | Get cart + total |
| POST | `/api/cart/add` | Add item `{product_id, quantity}` |
| PUT | `/api/cart/update` | Update qty `{product_id, quantity}` |
| DELETE | `/api/cart/remove` | Remove item `{product_id}` |
| DELETE | `/api/cart/clear` | Empty cart |

### Orders (requires login)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders/place` | Place order `{payment_method}` |
| GET | `/api/orders` | Get order history |
| PUT | `/api/orders/<id>/cancel` | Cancel pending order |

### Wishlist (requires login)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wishlist` | Get wishlist items |
| GET | `/api/wishlist/ids` | Get product IDs only |
| POST | `/api/wishlist/add` | Add `{product_id}` |
| DELETE | `/api/wishlist/remove` | Remove `{product_id}` |

### Admin (requires admin session)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/` | Dashboard page |
| GET | `/admin/stats` | User/product/order stats |
| GET | `/admin/orders` | All orders |
| POST | `/admin/products` | Add product |
| PUT | `/admin/products/<id>` | Update product |
| DELETE | `/admin/products/<id>` | Delete product |

---

## 🐛 Troubleshooting

**"Can't connect to MySQL"** → Check your password in `db.py`. Make sure MySQL service is running.

**"Module not found"** → Run `pip install -r requirements.txt` again.

**Images not showing** → Make sure all images are in `static/images/`. The app serves them at `/static/images/<filename>`.

**Session not persisting** → Flask-Session creates a `flask_session/` folder in your project. Make sure the directory is writable.
