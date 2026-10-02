from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from mandarake_watcher.scraper import Item


DB_PATH = Path("mandarake_watcher.db")


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_items (
                keyword TEXT NOT NULL,
                item_code TEXT NOT NULL,
                title TEXT NOT NULL,
                price TEXT,
                shop TEXT,
                url TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                PRIMARY KEY (keyword, item_code)
            )
            """
        )


def keyword_has_history(keyword: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT 1
            FROM seen_items
            WHERE keyword = ?
            LIMIT 1
            """,
            (keyword,),
        )

        return cursor.fetchone() is not None


def save_items(
    keyword: str,
    items: list[Item],
) -> list[Item]:

    initialize_database()

    first_run = not keyword_has_history(keyword)

    new_items: list[Item] = []

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        for item in items:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO seen_items (
                    keyword,
                    item_code,
                    title,
                    price,
                    shop,
                    url,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    keyword,
                    item.item_code,
                    item.title,
                    item.price,
                    item.shop,
                    item.url,
                    now,
                    now,
                ),
            )

            if cursor.rowcount == 1:
                new_items.append(item)

            connection.execute(
                """
                UPDATE seen_items
                SET
                    title = ?,
                    price = ?,
                    shop = ?,
                    url = ?,
                    last_seen = ?
                WHERE
                    keyword = ?
                    AND item_code = ?
                """,
                (
                    item.title,
                    item.price,
                    item.shop,
                    item.url,
                    now,
                    keyword,
                    item.item_code,
                ),
            )

    if first_run:
        print(
            f"Initial baseline created for "
            f"'{keyword}' with {len(items)} items."
        )
        return []

    return new_items