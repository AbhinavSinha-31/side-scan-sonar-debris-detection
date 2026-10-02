import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "sonar_debris.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

for table_name in ['sonar_files', 'processing_runs', 'detections', 'shadow_analysis', 'geolocations', 'priority_scores']:
    try:
        c.execute(f"SELECT COUNT(*) FROM [{table_name}]")
        count = c.fetchone()[0]
        print(f"{table_name}: {count} rows")
    except Exception as e:
        print(f"{table_name}: ERROR - {e}")

conn.close()