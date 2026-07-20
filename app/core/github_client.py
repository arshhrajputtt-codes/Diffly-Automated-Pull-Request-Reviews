import base64

import httpx

from app.core.config import settings
from app.core.exceptions import GitHubApiError

HEADERS_BASE = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = settings.GITHUB_API_URL

    def _headers(self) -> dict:
        if not self.token:
            raise GitHubApiError("GITHUB_TOKEN is not configured")
        return {**HEADERS_BASE, "Authorization": f"Bearer {self.token}"}

    def get_pr_files(self, repo_full_name: str, pr_number: int) -> list[dict]:
        """
        Returns GitHub's changed-files list for a PR — each entry includes
        filename, status (added/modified/removed), and a `patch` field with
        that file's unified diff hunk (GitHub computes this for us; no need
        to shell out to `git diff` ourselves).
        """
        url = f"{self.base_url}/repos/{repo_full_name}/pulls/{pr_number}/files"
        try:
            response = httpx.get(url, headers=self._headers(), params={"per_page": 100}, timeout=20.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GitHubApiError(f"{exc.response.status_code} fetching PR files: {exc.response.text}") from exc
        except httpx.RequestError as exc:
            raise GitHubApiError(str(exc)) from exc

        return response.json()

    def get_file_content(self, repo_full_name: str, path: str, ref: str) -> str | None:
        """
        Full content of a file at a given commit — used as extra context
        beyond just the diff hunk (a 3-line diff is hard to review without
        seeing the function it's part of). Returns None for files GitHub
        won't serve as text (binaries, or files too large for the contents API).
        """
        url = f"{self.base_url}/repos/{repo_full_name}/contents/{path}"
        try:
            response = httpx.get(url, headers=self._headers(), params={"ref": ref}, timeout=20.0)
            if response.status_code == 404:
                return None
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GitHubApiError(f"{exc.response.status_code} fetching file content: {exc.response.text}") from exc
        except httpx.RequestError as exc:
            raise GitHubApiError(str(exc)) from exc

        data = response.json()
        if data.get("encoding") != "base64" or "content" not in data:
            return None

        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None

    def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str) -> dict:
        """
        Posts a comment on the PR's conversation tab. GitHub treats every PR
        as an issue under the hood, so the "issues" comments endpoint is the
        correct one here — not a review-specific endpoint.
        """
        url = f"{self.base_url}/repos/{repo_full_name}/issues/{pr_number}/comments"
        try:
            response = httpx.post(url, headers=self._headers(), json={"body": body}, timeout=20.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GitHubApiError(f"{exc.response.status_code} posting comment: {exc.response.text}") from exc
        except httpx.RequestError as exc:
            raise GitHubApiError(str(exc)) from exc

        return response.json()
