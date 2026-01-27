from sqlalchemy import select

from app.core.db import db_session
from app.models.api_key import ApiKey

DEFAULT_KEYS = [
    "demo_key_1",
    "demo_key_2",
]

def main() -> None:
    with db_session() as db:
        for key in DEFAULT_KEYS:
            exists = db.execute(select(ApiKey).where(ApiKey.key == key)).scalar_one_or_none()
            if not exists:
                db.add(ApiKey(key=key, is_active=True))
    print("Seeded API keys: demo_key_1, demo_key_2")

if __name__ == "__main__":
    main()
