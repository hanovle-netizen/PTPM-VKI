import sqlite3

MAX_NAME = 256
MAX_MESSAGE = 8096


class DatabaseRepository:
    """Репозиторий сообщений форума (таблица comments)."""

    def __init__(self, path=":memory:"):
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                message TEXT NOT NULL
            )"""
        )
        self._conn.commit()

    @staticmethod
    def _check_id(comment_id):
        if isinstance(comment_id, bool) or not isinstance(comment_id, int):
            raise TypeError("id должен быть целым числом")

    @staticmethod
    def _check_text(value, limit, field):
        if not isinstance(value, str):
            raise TypeError(f"{field} должно быть строкой")
        if not value:
            raise ValueError(f"{field} не может быть пустым")
        if len(value) > limit:
            raise ValueError(f"{field} длиннее {limit} символов")

    def get_by_id(self, comment_id):
        self._check_id(comment_id)
        row = self._conn.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
        return dict(row) if row else None

    def get_by_name(self, username):
        rows = self._conn.execute(
            "SELECT * FROM comments WHERE name = ? ORDER BY id", (username,)
        ).fetchall()
        return [dict(r) for r in rows]

    def add(self, comment_id, username, message):
        self._check_id(comment_id)
        self._check_text(username, MAX_NAME, "name")
        self._check_text(message, MAX_MESSAGE, "message")
        try:
            self._conn.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                (comment_id, username, message),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"запись с id={comment_id} уже существует") from exc
        self._conn.commit()
        return True

    def update(self, comment_id, new_message):
        self._check_id(comment_id)
        self._check_text(new_message, MAX_MESSAGE, "message")
        cur = self._conn.execute(
            "UPDATE comments SET message = ? WHERE id = ?", (new_message, comment_id)
        )
        self._conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"запись с id={comment_id} не найдена")
        return True

    def delete(self, comment_id):
        self._check_id(comment_id)
        cur = self._conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def close(self):
        self._conn.close()
