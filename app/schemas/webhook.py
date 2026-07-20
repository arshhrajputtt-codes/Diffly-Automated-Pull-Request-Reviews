from pydantic import BaseModel


class GitHubUser(BaseModel):
    login: str


class GitHubBranchRef(BaseModel):
    sha: str | None = None
    ref: str


class GitHubPullRequest(BaseModel):
    number: int
    title: str
    html_url: str
    head: GitHubBranchRef
    base: GitHubBranchRef
    user: GitHubUser


class GitHubRepository(BaseModel):
    full_name: str


class PullRequestWebhookPayload(BaseModel):
    action: str
    pull_request: GitHubPullRequest
    repository: GitHubRepository
