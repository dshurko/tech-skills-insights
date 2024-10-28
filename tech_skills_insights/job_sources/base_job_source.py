import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import html2text

from tech_skills_insights.models import RawJob


class BaseJobSource(ABC):
    NEWLINES_PATTERN = re.compile(r"\n+")
    WHITESPACE_PATTERN = re.compile(r"^\s+|\s+$", re.MULTILINE)
    ESCAPED_CHAR_PATTERN = re.compile(r"^\\", re.MULTILINE)
    LEADING_HASH_PATTERN = re.compile(r"^#+\s?", re.MULTILINE)

    def __init__(self, category_to_url: dict[str, str]):
        self.category_to_url = category_to_url

    def retrieve_jobs_in_date_range(
        self, start_date: date, end_date: date
    ) -> list[RawJob]:
        jobs = []
        with ThreadPoolExecutor() as executor:
            category_futures = {
                executor.submit(
                    self._retrieve_category_jobs_in_date_range,
                    category,
                    start_date,
                    end_date,
                ): category
                for category in self.category_to_url
            }

            for future in as_completed(category_futures):
                try:
                    jobs.extend(future.result())
                except Exception as e:
                    category = category_futures[future]
                    print(f"Error fetching jobs for '{category}': {e}")

        return jobs

    @abstractmethod
    def _retrieve_category_jobs_in_date_range(
        self, category: str, start_date: date, end_date: date
    ) -> list[RawJob]:
        pass

    def _convert_html_to_text(self, html_content: str) -> str:
        parser = html2text.HTML2Text()
        parser.body_width = 0
        parser.ignore_emphasis = True
        parser.ignore_links = True

        text_content = parser.handle(html_content)
        text_content = self.NEWLINES_PATTERN.sub("\n", text_content).strip()
        text_content = self.WHITESPACE_PATTERN.sub("", text_content)
        text_content = self.ESCAPED_CHAR_PATTERN.sub("", text_content)
        text_content = self.LEADING_HASH_PATTERN.sub("", text_content)

        return text_content
