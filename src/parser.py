import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Accept-Language": "ru,en;q=0.8",
}


class ForumParser:
    """Парсер страницы форума: пост = div.post[data-post-id] c .post-author и .post-body."""

    def __init__(self, session=None, timeout=10):
        self.session = session or requests
        self.timeout = timeout

    def fetch(self, url):
        response = self.session.get(url, headers=HEADERS, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    @staticmethod
    def parse_html(html):
        soup = BeautifulSoup(html, "lxml")
        result = []
        for post in soup.select("div.post[data-post-id]"):
            author = post.select_one(".post-author")
            body = post.select_one(".post-body")
            if author is None or body is None:
                continue
            try:
                post_id = int(post["data-post-id"])
            except ValueError:
                continue
            result.append({
                "id": post_id,
                "name": author.get_text(strip=True),
                "message": body.decode_contents().strip(),
            })
        return result

    def parse_page(self, url):
        return self.parse_html(self.fetch(url))

    @staticmethod
    def save_to_db(parsed_data, repository):
        """Сохраняет посты; уже существующие id пропускает. Возвращает число добавленных."""
        saved = 0
        for item in parsed_data:
            if repository.get_by_id(item["id"]) is not None:
                continue
            repository.add(item["id"], item["name"], item["message"])
            saved += 1
        return saved
