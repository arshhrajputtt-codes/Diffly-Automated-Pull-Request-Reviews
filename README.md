<div align="center">

# ◈ Diffly — Automated Pull Request Reviews

An AI code reviewer that lives inside your GitHub workflow. Open a PR, get a real review comment — automatically.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![GitHub API](https://img.shields.io/badge/GitHub_API-181717?style=flat-square&logo=github&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)

</div>

---

## What is Diffly?

Diffly watches a repository for pull requests, fetches the actual diff and surrounding file context, sends it to an LLM for review, and posts the result back as a real comment on the PR — the same way a human reviewer would, just automatic and immediate.

No copy-pasting diffs into a chat window. No separate tool to check. It shows up exactly where code review already happens.

## Features

**🔒 Verified Webhooks**
- Every GitHub webhook is cryptographically verified (HMAC-SHA256) before anything in it is trusted
- Constant-time signature comparison — not vulnerable to timing attacks

**🤖 Automated Review Pipeline**
- Fetches the real PR diff via GitHub's API (not a hand-rolled `git diff`)
- Pulls full content of changed files as extra context, so a 3-line diff isn't reviewed in isolation
- Generates a structured review with an LLM and posts it back as a genuine PR comment

**⚙️ Async by Design**
- Webhook ingestion and review generation are decoupled — GitHub gets an instant response, the review runs in the background
- Full status tracking per request: received → processing → completed / failed

**📊 Live Dashboard**
- React dashboard showing every review request and its status in real time
- Click into any request to read the generated review, with a link to the actual posted GitHub comment

## Architecture
GitHub PR event
│
▼
┌──────────────────┐ verify signature (HMAC-SHA256)
│ Webhook Service │───────────────────────────────────► reject if invalid
└─────────┬──────────┘
│ stored + queued
▼
┌──────────────────┐ GitHub API: diff + file context
│ Review Engine │───────────────────────────────────►
└─────────┬──────────┘
│ LLM: generate review
▼
┌──────────────────┐ GitHub API: post comment
│ GitHub Integration │───────────────────────────────────► real PR comment
└─────────┬──────────┘
│
▼
┌──────────────────┐
│ Dashboard │ live status + review content
└──────────────────┘

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Integration | GitHub REST API, HMAC signature verification |
| LLM | Ollama (local, free) or Groq (cloud, free) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, TanStack Query |

## Getting Started

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set GITHUB_WEBHOOK_SECRET and GITHUB_TOKEN in .env
uvicorn app.main:app --reload --port 8010

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

By default, reviews are generated locally through [Ollama](https://ollama.com) — no API keys, no cost. See `.env.example` for the Groq cloud alternative.

### Testing locally with a real webhook

Your machine has no public URL by default, so GitHub can't reach it directly. Use [smee.io](https://smee.io) to relay:

```bash
npm install --global smee-client
smee -u <your-smee-channel-url> -t http://localhost:8010/webhooks/github
```

Then point a GitHub webhook (Settings → Webhooks) at your smee.io URL, with `GITHUB_WEBHOOK_SECRET` matching your `.env`.

## Known Limitations (v1)

- Uses FastAPI `BackgroundTasks`, not Celery/Redis — a failed review doesn't automatically retry
- Review context is full changed-file content, not a true embedding-based RAG search across the whole repo
- Authenticates via Personal Access Token — posts as the token owner's account, not a separate bot identity
- No auth on the dashboard/API yet — built for personal/local use

## Status

Built and manually verified end-to-end against a real GitHub repository — a real pull request, a real posted review comment. Automated tests and a live deployment are in progress.

