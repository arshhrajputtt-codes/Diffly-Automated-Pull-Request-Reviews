# Diffly

AI-powered GitHub pull request reviewer. GitHub webhook → fetch diff + context → LLM review → posted back as a PR comment.

## Architecture

- **Backend** (`/app`) — FastAPI. Receives and verifies GitHub webhooks, runs the review pipeline as a background task, exposes a read API for the dashboard.
- **Frontend** (`/frontend`) — React + Vite + TypeScript. Read-only dashboard showing review requests and their generated reviews. No auth yet — matches the backend, which also has none (single-user local tool for now).

## Backend setup

```
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # Mac/Linux: cp .env.example .env
```

Edit `.env`:
- `GITHUB_WEBHOOK_SECRET` — any random string; you'll enter this exact value on GitHub's webhook config
- `GITHUB_TOKEN` — a Personal Access Token with `repo` scope (GitHub → Settings → Developer settings → Personal access tokens)
- `LLM_PROVIDER` — `ollama` (free, default, needs Ollama running locally) or `anthropic` (paid, needs `ANTHROPIC_API_KEY`)

```
uvicorn app.main:app --reload --port 8010
```

## Frontend setup

```
cd frontend
npm install
copy .env.example .env
npm run dev
```

Opens on `http://localhost:5180`. Needs the backend running on port 8010 (or update `VITE_DIFFLY_API_URL` if you changed the backend's port).

## Testing locally with a real GitHub webhook

Your machine has no public URL, so GitHub can't reach `localhost:8010` directly — smee.io (GitHub's own recommended tool for this) relays it:

1. Go to smee.io, click "Start a new channel", copy the URL
2. `npm install --global smee-client`
3. `smee -u <your-smee-url> -t http://localhost:8010/webhooks/github`
4. On GitHub: any repo you own → Settings → Webhooks → Add webhook
   - Payload URL: your smee.io URL
   - Content type: `application/json`
   - Secret: exactly matching `GITHUB_WEBHOOK_SECRET` in your `.env`
   - Events: "Pull requests" only
5. Open or update a PR on that repo
6. Watch it appear in the dashboard, move through Received → Reviewing → Reviewed, and check the actual PR on GitHub for the posted comment

## Known limitations (v1, documented rather than hidden)

- **No Celery/Redis** — uses FastAPI's `BackgroundTasks`. A failed review just sits at `failed`; nothing retries it automatically.
- **RAG-lite, not full RAG** — context is the full content of changed files, not a vector search across the whole repository. No embeddings pipeline.
- **Personal Access Token, not a GitHub App** — posts comments as your GitHub account, not as a separate bot identity. Only works on repos you have access to; not installable on other people's repos.
- **No auth on the API or dashboard** — anyone who can reach the backend can read all review requests. Fine for local/personal use, not for deploying anywhere public.
- **Never tested against a real GitHub webhook** — built and compile-checked, not yet run end-to-end. The smee.io flow above is the first real test.
