from __future__ import annotations

import os
import time
from datetime import datetime

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from thg_exchange.models import enums


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def main() -> None:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/thg_exchange_db")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!").strip()
    admin_user_id = os.getenv("ADMIN_USER_ID", "admin_1").strip()

    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    if db is None:
        db = client["thg_exchange_db"]

    users = db.users

    existing_admin = users.find_one({"role": enums.USER_ROLE_ADMIN})
    if existing_admin:
        return

    users.insert_one(
        {
            "userId": admin_user_id,
            "email": admin_email,
            "passwordHash": generate_password_hash(admin_password),
            "firstName": "Admin",
            "lastName": "User",
            "fullName": "Admin User",
            "role": enums.USER_ROLE_ADMIN,
            "verificationStatus": enums.VERIF_VERIFIED,
            "walletBalance": 0.0,
            "createdAt": now_iso(),
        }
    )


if __name__ == "__main__":
    main()
