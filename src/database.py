import sqlite3


def _key(value):
    """Единый вид стороны: 3, '3', '3,0' и 3.0 дают один и тот же ключ."""
    try:
        return repr(float(str(value).strip().replace(",", ".")))
    except ValueError:
        return str(value).strip()


class TriangleDatabase:
    """Хранилище результатов; запись идентифицируется тремя сторонами."""

    def __init__(self, path=":memory:"):
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS triangles (
                side1 TEXT NOT NULL,
                side2 TEXT NOT NULL,
                side3 TEXT NOT NULL,
                triangle_type TEXT NOT NULL,
                error_message TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (side1, side2, side3)
            )"""
        )
        self._conn.commit()

    def add(self, side1, side2, side3, triangle_type, error_message=""):
        self._conn.execute(
            "INSERT OR REPLACE INTO triangles VALUES (?, ?, ?, ?, ?)",
            (_key(side1), _key(side2), _key(side3), triangle_type, error_message),
        )
        self._conn.commit()

    def get(self, side1, side2, side3):
        """Возвращает (тип, сообщение) или None, если записи нет."""
        row = self._conn.execute(
            "SELECT triangle_type, error_message FROM triangles "
            "WHERE side1 = ? AND side2 = ? AND side3 = ?",
            (_key(side1), _key(side2), _key(side3)),
        ).fetchone()
        return row

    def delete(self, side1, side2, side3):
        """Удаляет запись, возвращает True, если она существовала."""
        cur = self._conn.execute(
            "DELETE FROM triangles WHERE side1 = ? AND side2 = ? AND side3 = ?",
            (_key(side1), _key(side2), _key(side3)),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def close(self):
        self._conn.close()
