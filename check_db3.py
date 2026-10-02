import sqlite3
import os
from pathlib import Path

root = Path(r"C:\Users\RISHABH SHARMA\OneDrive\Documents\SIH MAIN")

# Check the root sonar_debris.db
db_path = root / "sonar_debris.db"
conn = sqlite3.connect(str(db_path))
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM detections")
print(f"root sonar_debris.db detections: {c.fetchone()[0]}")
conn.close()

# Also check for any .db under data/ or backend/
for p in root.rglob("*.db"):
    if "site-packages" in str(p): continue
    try:
        conn = sqlite3.connect(str(p))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM detections")
        cnt = c.fetchone()[0]
        print(f"{p} : detections={cnt}")
        conn.close()
    except Exception as e:
        print(f"{p}: {e}")