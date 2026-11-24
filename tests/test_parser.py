import os
import unittest
from unittest.mock import MagicMock

import requests

from src.database import DatabaseRepository
from src.parser import HEADERS, ForumParser

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "forum_page.html")


def load_fixture():
    with open(FIXTURE, encoding="utf-8") as f:
        return f.read()


class TestForumParser(unittest.TestCase):
    def test_parse_html_extracts_id_author_and_message(self):
        posts = ForumParser.parse_html(load_fixture())
        self.assertEqual(posts[0], {"id": 101, "name": "ivan", "message": "Привет, <b>всем</b>!"})
        self.assertEqual(posts[1]["name"], "maria")

    def test_parse_html_skips_broken_posts(self):
        posts = ForumParser.parse_html(load_fixture())
        self.assertEqual([p["id"] for p in posts], [101, 102, 103])

    def test_parse_page_sends_user_agent_and_parses_response(self):
        session = MagicMock()
        session.get.return_value.text = load_fixture()
        posts = ForumParser(session=session).parse_page("http://forum.test/t/1")
        args, kwargs = session.get.call_args
        self.assertEqual(args[0], "http://forum.test/t/1")
        self.assertIn("User-Agent", kwargs["headers"])
        self.assertEqual(kwargs["headers"], HEADERS)
        self.assertEqual(len(posts), 3)

    def test_parse_page_propagates_http_error(self):
        session = MagicMock()
        session.get.return_value.raise_for_status.side_effect = requests.HTTPError("404")
        with self.assertRaises(requests.HTTPError):
            ForumParser(session=session).parse_page("http://forum.test/missing")

    def test_save_to_db_stores_posts_and_skips_existing(self):
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo.close)
        posts = ForumParser.parse_html(load_fixture())
        self.assertEqual(ForumParser.save_to_db(posts, repo), 3)
        self.assertEqual(ForumParser.save_to_db(posts, repo), 0)
        self.assertEqual(len(repo.get_by_name("ivan")), 2)
        self.assertEqual(repo.get_by_id(102)["message"], "Вторая реплика<br/>с переносом")


if __name__ == "__main__":
    unittest.main()
