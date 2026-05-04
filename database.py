import aiosqlite
import datetime
import json

DB_PATH = "booth_bot.db"

# SQL vaicājumi datu bāzes inicializēšanai
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Lietotāju tabula
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'EN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Pasūtījumu tabula
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                length REAL,
                width REAL,
                layout_type TEXT,
                construction_type TEXT,
                materials TEXT,
                finishing TEXT,
                equipment TEXT,
                services TEXT,
                total_price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        async with db.execute("PRAGMA table_info(orders)") as cursor:
            existing_columns = [row[1] for row in await cursor.fetchall()]

        missing_columns = [
            ("layout_type", "TEXT"),
            ("finishing", "TEXT"),
            ("services", "TEXT")
        ]

        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                await db.execute(f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}")

        await db.commit()

async def add_user(user_id, username, full_name, language):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username, full_name, language) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, language)
        )
        await db.commit()

async def save_order(user_id, length, width, layout_type, construction_type, materials, finishing, equipment, services, total_price):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO orders (user_id, length, width, layout_type, construction_type, materials, finishing, equipment, services, total_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                length,
                width,
                layout_type,
                construction_type,
                json.dumps(materials),
                json.dumps(finishing),
                json.dumps(equipment),
                json.dumps(services),
                total_price
            )
        )
        await db.commit()

async def get_user_orders(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,)) as cursor:
            return await cursor.fetchall()

async def get_user_order_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*), COALESCE(SUM(total_price), 0) FROM orders WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return {
                "count": row[0],
                "total": row[1]
            }

async def get_order_by_id(user_id, order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? AND order_id = ?",
            (user_id, order_id)
        ) as cursor:
            return await cursor.fetchone()

async def get_order_stats(days=7):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*), COALESCE(SUM(total_price), 0) FROM orders WHERE created_at >= datetime('now', ?)",
            (f"-{days} days",)
        ) as cursor:
            row = await cursor.fetchone()
            return {
                "count": row[0],
                "total": row[1]
            }
