import unittest

from src.database import MAX_MESSAGE, MAX_NAME, DatabaseRepository


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = DatabaseRepository(":memory:")
        self.addCleanup(self.repo.close)


class TestAdd(DatabaseTestCase):
    def test_add_new_record_succeeds(self):
        self.assertTrue(self.repo.add(1, "ivan", "текст"))
        self.assertEqual(self.repo.get_by_id(1), {"id": 1, "name": "ivan", "message": "текст"})

    def test_add_duplicate_id_raises_value_error(self):
        self.repo.add(1, "ivan", "a")
        with self.assertRaises(ValueError):
            self.repo.add(1, "other", "b")

    def test_add_rejects_wrong_types(self):
        with self.assertRaises(TypeError):
            self.repo.add("1", "ivan", "a")
        with self.assertRaises(TypeError):
            self.repo.add(1, 5, "a")
        with self.assertRaises(TypeError):
            self.repo.add(True, "ivan", "a")

    def test_add_rejects_too_long_and_empty_strings(self):
        with self.assertRaises(ValueError):
            self.repo.add(1, "x" * (MAX_NAME + 1), "a")
        with self.assertRaises(ValueError):
            self.repo.add(1, "ivan", "x" * (MAX_MESSAGE + 1))
        with self.assertRaises(ValueError):
            self.repo.add(1, "", "a")

    def test_add_accepts_maximum_length(self):
        self.assertTrue(self.repo.add(1, "x" * MAX_NAME, "y" * MAX_MESSAGE))


class TestGetById(DatabaseTestCase):
    def test_get_by_id_returns_existing_record(self):
        self.repo.add(5, "ivan", "hi")
        self.assertEqual(self.repo.get_by_id(5)["name"], "ivan")

    def test_get_by_id_returns_none_for_missing(self):
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_id_rejects_non_integer(self):
        with self.assertRaises(TypeError):
            self.repo.get_by_id("5")


class TestGetByName(DatabaseTestCase):
    def test_get_by_name_returns_all_user_records(self):
        self.repo.add(1, "ivan", "a")
        self.repo.add(2, "maria", "b")
        self.repo.add(3, "ivan", "c")
        self.assertEqual([r["id"] for r in self.repo.get_by_name("ivan")], [1, 3])

    def test_get_by_name_returns_empty_list_for_unknown_user(self):
        self.assertEqual(self.repo.get_by_name("nobody"), [])


class TestUpdate(DatabaseTestCase):
    def test_update_changes_message(self):
        self.repo.add(1, "ivan", "old")
        self.assertTrue(self.repo.update(1, "new"))
        self.assertEqual(self.repo.get_by_id(1)["message"], "new")

    def test_update_missing_id_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.repo.update(42, "text")

    def test_update_rejects_too_long_message(self):
        self.repo.add(1, "ivan", "old")
        with self.assertRaises(ValueError):
            self.repo.update(1, "x" * (MAX_MESSAGE + 1))
        self.assertEqual(self.repo.get_by_id(1)["message"], "old")


class TestDelete(DatabaseTestCase):
    def test_delete_removes_record(self):
        self.repo.add(1, "ivan", "a")
        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_record_returns_false(self):
        self.assertFalse(self.repo.delete(1))


if __name__ == "__main__":
    unittest.main()
