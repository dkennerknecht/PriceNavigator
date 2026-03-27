from __future__ import annotations

from app.core.database import SessionLocal
from app.services.seeding import seed_database


def main() -> None:
    with SessionLocal() as session:
        seed_database(session)


if __name__ == "__main__":
    main()
