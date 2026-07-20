from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import GitHubApiError, ProviderError
from app.core.github_client import GitHubClient
from app.models.review import Review
from app.models.review_request import ReviewRequest, ReviewStatus
from app.repositories.review_repository import ReviewRepository
from app.repositories.review_request_repository import ReviewRequestRepository
from app.services.llm_service import LLMService

SYSTEM_PROMPT = """You are an experienced senior software engineer doing a pull request code review.

Review the diff below for:
- Bugs or logic errors
- Security issues
- Unclear or risky changes
- Missed edge cases

Be specific and reference actual lines/functions. If the change looks fine, say so briefly — \
don't invent issues to seem thorough. Keep the review concise: a few focused points beat a long \
list of minor nitpicks. Format as a short bulleted list, GitHub-Markdown-flavored."""

USER_PROMPT_TEMPLATE = """Pull request: "{title}"

## Changed files (diff)
{diff_section}

## Additional file context
{context_section}
"""


class ReviewService:
    def __init__(
        self,
        review_request_repository: ReviewRequestRepository | None = None,
        review_repository: ReviewRepository | None = None,
        github_client: GitHubClient | None = None,
        llm_service: LLMService | None = None,
    ):
        self.review_request_repository = review_request_repository or ReviewRequestRepository()
        self.review_repository = review_repository or ReviewRepository()
        self.github_client = github_client or GitHubClient()
        self.llm_service = llm_service or LLMService()

    def run_review(self, db: Session, review_request_id: int) -> None:
        """
        Entry point for the background task. Deliberately swallows and
        records its own errors (via ReviewStatus.FAILED) rather than
        raising — this runs detached from the webhook's HTTP response, so
        there's no request left to return an error to; the only place a
        failure can surface is the status column and error_message.
        """
        review_request = self.review_request_repository.get_by_id(db, review_request_id)
        if not review_request:
            return  # nothing to do — shouldn't happen, but not worth crashing a background task over

        review_request.status = ReviewStatus.PROCESSING
        self.review_request_repository.update(db, review_request)

        try:
            content, usage = self._generate_review(review_request)
            comment = self.github_client.post_pr_comment(
                review_request.repo_full_name, review_request.pr_number, content
            )

            review = Review(
                review_request_id=review_request.id,
                content=content,
                model=usage["model"],
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                github_comment_url=comment.get("html_url"),
            )
            self.review_repository.create(db, review)

            review_request.status = ReviewStatus.COMPLETED
            self.review_request_repository.update(db, review_request)

        except (GitHubApiError, ProviderError) as exc:
            review_request.status = ReviewStatus.FAILED
            review_request.error_message = str(exc)[:500]
            self.review_request_repository.update(db, review_request)

    def _generate_review(self, review_request: ReviewRequest) -> tuple[str, dict]:
        files = self.github_client.get_pr_files(review_request.repo_full_name, review_request.pr_number)

        diff_section = self._build_diff_section(files)
        context_section = self._build_context_section(review_request, files)

        user_prompt = USER_PROMPT_TEMPLATE.format(
            title=review_request.pr_title,
            diff_section=diff_section,
            context_section=context_section,
        )

        result = self.llm_service.complete(SYSTEM_PROMPT, user_prompt)
        return result["content"], result

    def _build_diff_section(self, files: list[dict]) -> str:
        parts = []
        for f in files:
            patch = f.get("patch")  # GitHub omits `patch` for binary/very large files
            if not patch:
                parts.append(f"### {f['filename']} ({f['status']})\n(no text diff available)")
                continue
            parts.append(f"### {f['filename']} ({f['status']})\n```diff\n{patch}\n```")
        return "\n\n".join(parts) if parts else "(no changed files)"

    def _build_context_section(self, review_request: ReviewRequest, files: list[dict]) -> str:
        """
        RAG-lite for v1: rather than a separate embedding/vector-search
        pipeline (which would mean standing up another Postgres+pgvector,
        redundant with what Vynera already needed), context here is the
        full content of each changed file at the PR's head commit — enough
        to review a 3-line diff without seeing only those 3 lines in
        isolation. A real semantic search over the whole repo (not just
        changed files) would be the next upgrade, not a v1 requirement.
        """
        candidates = [f for f in files if f["status"] != "removed"][: settings.MAX_CONTEXT_FILES]
        parts = []

        for f in candidates:
            content = self.github_client.get_file_content(
                review_request.repo_full_name, f["filename"], review_request.head_sha
            )
            if content is None:
                continue
            # Cap individual file size in the prompt — a single huge
            # generated/vendored file shouldn't crowd out everything else.
            truncated = content[:4000]
            parts.append(f"#### {f['filename']}\n```\n{truncated}\n```")

        return "\n\n".join(parts) if parts else "(no additional context retrieved)"
