#!/bin/bash
set -e

echo "Waiting for MongoDB"
python - <<'PY'
import os, time
from pymongo import MongoClient

uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/thg_exchange_db")
client = MongoClient(uri, serverSelectionTimeoutMS=2000)

for _ in range(30):
    try:
        client.admin.command("ping")
        print("MongoDB is ready")
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("MongoDB not reachable")
PY

echo "Seeding default admin if needed"
python -m thg_exchange.scripts.seed_admin

echo "Starting web server"
exec flask --app thg_exchange.webapp run --host 0.0.0.0 --port 5000
