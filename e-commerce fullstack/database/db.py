import mysql.connector
from mysql.connector import Error
import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'ricky'),
    'database': os.environ.get('DB_NAME', 'flipkart_db'),
    'autocommit': True
}

def get_db():
    """Get a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Create all tables if they don't exist."""
    # First connect without database to create it if needed
    try:
        config_no_db = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
        conn = mysql.connector.connect(**config_no_db)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error creating database: {e}")
        raise

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            image VARCHAR(300),
            description TEXT,
            stock INT DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE KEY unique_cart_item (user_id, product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
            payment_method VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            product_name VARCHAR(200),
            quantity INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE KEY unique_wishlist_item (user_id, product_id)
        )
    """)

    # Seed products if none exist
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        _seed_products(cursor)

    cursor.close()
    conn.close()
    print("Database initialized successfully.")

def _seed_products(cursor):
    """Insert default products matching the existing static images."""
    products = [
        # Menswear
        ("Men's T-Shirt", "Menswear", 499, "tshirt.jpeg", "Classic cotton t-shirt for everyday wear"),
        ("Men's Polo Shirt", "Menswear", 599, "men polo shirt.webp", "Comfortable polo shirt for casual outings"),
        ("Men's Casual Shirt", "Menswear", 699, "men casual shirt.jpeg", "Stylish casual shirt for weekends"),
        ("Men's Formal Shirt", "Menswear", 799, "men formal shirt.jpg", "Crisp formal shirt for the office"),
        ("Men's Jeans", "Menswear", 999, "men jeans.jpeg", "Slim fit denim jeans"),
        ("Men's Cargo Pants", "Menswear", 1099, "men cargo.jpg", "Utility cargo pants with multiple pockets"),
        ("Men's Track Pants", "Menswear", 949, "men track.avif", "Comfortable track pants for workouts"),
        ("Men's Hoodie", "Menswear", 1199, "men hoddie.jpg", "Warm fleece hoodie for winter"),
        ("Men's Sweatshirt", "Menswear", 899, "men sweatshirt.jpeg", "Casual sweatshirt for cool days"),
        ("Men's Jacket", "Menswear", 1499, "men jacket.webp", "Stylish jacket for outdoor adventures"),
        # Womenswear
        ("Women's Kurti", "Womenswear", 699, "women kurti.jpg", "Ethnic kurti for traditional occasions"),
        ("Trendy Kurti", "Womenswear", 799, "trendy kurti.jpg", "Modern printed kurti"),
        ("Women's Top", "Womenswear", 549, "women top.webp", "Casual top for everyday style"),
        ("Women's T-Shirt", "Womenswear", 499, "women tshirt.jpeg", "Basic cotton t-shirt"),
        ("Maxi Dress", "Womenswear", 1199, "maxi dress.jpeg", "Elegant maxi dress for special occasions"),
        ("Saree", "Womenswear", 1499, "saree.jpeg", "Beautiful traditional saree"),
        ("Women's Jacket", "Womenswear", 1399, "women jacket.webp", "Stylish jacket for women"),
        ("Women's Formal Shirt", "Womenswear", 799, "women formalshirt.webp", "Professional formal shirt"),
        ("Women's Hoodie", "Womenswear", 999, "women hoddie.jpg", "Cozy hoodie for women"),
        ("Leggings", "Womenswear", 449, "leggin.jpeg", "Comfortable stretch leggings"),
        ("Women's Skirt", "Womenswear", 649, "women skrit.jpeg", "Flowy casual skirt"),
        ("Women's Plazzo", "Womenswear", 749, "women plazzo.jpeg", "Wide-leg palazzo pants"),
        # Electronics
        ("Laptop", "Electronics", 45999, "laptop.jpeg", "High-performance laptop for work and play"),
        ("Smartphone", "Electronics", 18999, "smart phone.jpeg", "Latest Android smartphone"),
        ("Smartwatch", "Electronics", 4999, "smartwatch.jpeg", "Feature-rich smartwatch"),
        ("Bluetooth Headphones", "Electronics", 2499, "bluetooth headphones.jpeg", "Wireless over-ear headphones"),
        ("Bluetooth Speaker", "Electronics", 1999, "bluetooth speaker.webp", "Portable wireless speaker"),
        ("Keyboard", "Electronics", 1299, "keyboard.jpeg", "Mechanical gaming keyboard"),
        ("Wireless Mouse", "Electronics", 799, "wireless mouse.jpeg", "Ergonomic wireless mouse"),
        ("Powerbank", "Electronics", 1299, "powerbank.jpeg", "20000mAh fast charging powerbank"),
        ("Webcam", "Electronics", 1599, "webcam.jpg", "Full HD webcam for video calls"),
        ("Tablet", "Electronics", 12999, "tablet.avif", "10-inch Android tablet"),
        # Home Appliances
        ("Air Fryer", "Home Appliances", 3999, "air fryer.jpeg", "Healthy cooking air fryer"),
        ("Electronic Kettle", "Home Appliances", 899, "electronic kettle.jpeg", "Fast boiling electric kettle"),
        ("Induction Cooktop", "Home Appliances", 1799, "induction cooktop.avif", "Energy efficient induction stove"),
        ("Mixer Grinder", "Home Appliances", 2499, "mixer grinder.jpeg", "Powerful 3-jar mixer grinder"),
        ("Oven", "Home Appliances", 4499, "oven.jpeg", "Microwave oven with grill"),
        ("Vacuum Cleaner", "Home Appliances", 3299, "vaccum cleaner.jpg", "Powerful suction vacuum cleaner"),
        ("Steam Iron", "Home Appliances", 999, "steam iron.jpeg", "Ceramic plate steam iron"),
        ("Ceiling Fan", "Home Appliances", 1799, "ceiling fan.jpeg", "Energy-saving ceiling fan"),
        ("Room Heater", "Home Appliances", 2199, "room heater.jpg", "Portable room heater"),
        ("Table Lamp", "Home Appliances", 799, "table lamp.jpeg", "LED table lamp with dimmer"),
        # Footwear
        ("Canvas Shoes", "Footwear", 999, "canvas shoes.jpg", "Casual canvas sneakers"),
    ]

    sql = """INSERT INTO products (name, category, price, image, description) VALUES (%s, %s, %s, %s, %s)"""
    cursor.executemany(sql, products)
    print(f"Seeded {len(products)} products.")
