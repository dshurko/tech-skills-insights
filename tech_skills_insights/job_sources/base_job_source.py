import re
from abc import ABC, abstractmethod
from datetime import date

import html2text

from tech_skills_insights.models import RawJob


class BaseJobSource(ABC):
    NEWLINES_PATTERN = re.compile(r"\n+")
    WHITESPACE_PATTERN = re.compile(r"^\s+|\s+$", re.MULTILINE)
    ESCAPED_CHAR_PATTERN = re.compile(r"^\\", re.MULTILINE)
    LEADING_HASH_PATTERN = re.compile(r"^#+\s?", re.MULTILINE)

    def __init__(
        self, category: str, category_url_part: str, start_date: date, end_date: date
    ):
        self.category = category
        self.category_url_part = category_url_part
        self.start_date = start_date
        self.end_date = end_date

    @abstractmethod
    def retrieve_jobs(self) -> list[RawJob]:
        pass

    def _convert_html_to_text(self, html_content: str) -> str:
        parser = html2text.HTML2Text()
        parser.body_width = 0
        parser.ignore_emphasis = True
        parser.ignore_links = True

        text_content = parser.handle(html_content)
        text_content = self.NEWLINES_PATTERN.sub("\n", text_content)
        text_content = self.WHITESPACE_PATTERN.sub("", text_content)
        text_content = self.ESCAPED_CHAR_PATTERN.sub("", text_content)
        text_content = self.LEADING_HASH_PATTERN.sub("", text_content)

        return text_content
