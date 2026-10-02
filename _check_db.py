import sqlite3
conn = sqlite3.connect('sonar_debris.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"  {t[0]}: {cursor.fetchone()[0]} rows")
conn.close()
