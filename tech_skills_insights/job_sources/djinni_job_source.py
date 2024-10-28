from datetime import date, datetime

import requests

from tech_skills_insights.job_sources.base_job_source import BaseJobSource
from tech_skills_insights.models import RawJob


class DjinniJobSource(BaseJobSource):
    BASE_API_URL = "https://djinni.co/api/jobs/"

    def _retrieve_category_jobs_in_date_range(
        self, category: str, start_date: date, end_date: date
    ) -> list[RawJob]:
        jobs = []
        offset = 0

        while True:
            response = requests.get(
                self.BASE_API_URL,
                params={"category": category, "offset": offset},
            )
            response.raise_for_status()
            data = response.json()
            job_results = data["results"]

            for job_data in job_results:
                published_at = datetime.fromisoformat(job_data["published"]).date()

                if published_at < start_date:
                    return jobs

                if start_date <= published_at <= end_date:
                    jobs.append(
                        RawJob(
                            title=job_data["title"],
                            company=job_data["company_name"],
                            category=category,
                            description=self._convert_html_to_text(
                                job_data["long_description"]
                            ),
                            published_at=published_at,
                            url=f"https://djinni.co/jobs/{job_data['slug']}/",
                            source="djinni",
                        )
                    )

            offset += len(job_results)
            if offset >= data["count"] or not job_results:
                break

        return jobs
