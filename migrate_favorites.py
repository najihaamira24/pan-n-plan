import sqlite3

def migrate():
    conn = sqlite3.connect('recipe_book.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='favorites'")
    table_exists = c.fetchone()

    if table_exists:
        print("✅ Tabel 'favorites' sudah ada, tidak perlu migrasi.")
    else:
        c.execute('''CREATE TABLE favorites (
                        user_id INTEGER,
                        recipe_id INTEGER,
                        PRIMARY KEY (user_id, recipe_id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (recipe_id) REFERENCES recipes(id)
                    )''')
        conn.commit()
        print("✅ Tabel 'favorites' berhasil ditambahkan.")

    conn.close()

if __name__ == '__main__':
    migrate()
