import sqlite3

def get_connection():
    return sqlite3.connect("users.db")

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock INTEGER DEFAULT 0,
        category TEXT,
        active INTEGER DEFAULT 0,
        last_updated TEXT,
        image_path TEXT
        );
    ''')
    # Stores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT
);
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    product TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY(client_id) REFERENCES clients(id)
);

""")
    # Junction table for product-store relationship
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_stores (
            product_id INTEGER,
            store_id INTEGER,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(store_id) REFERENCES stores(id),
            PRIMARY KEY(product_id, store_id)
        )
    ''')
    # cursor.execute("""DELETE FROM products""")
    conn.commit()
    conn.close()

def insert_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   (username, email, password))
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    return cursor.fetchone()


if __name__ == "__main__":
    create_tables()