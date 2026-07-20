import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { api } from '../lib/api'
import { StatusBadge } from '../components/StatusBadge'
import type { ReviewRequest } from '../lib/types'

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export function Dashboard() {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const { data: requests, isLoading } = useQuery({
    queryKey: ['review-requests'],
    queryFn: api.listReviewRequests,
    // Statuses move received -> processing -> completed/failed on their own
    // (the backend's background task drives that) — poll so the dashboard
    // reflects it without a manual refresh.
    refetchInterval: (query) => {
      const list = query.state.data
      const anyInFlight = list?.some((r) => r.status === 'received' || r.status === 'processing')
      return anyInFlight ? 3000 : 8000
    },
  })

  const selected = requests?.find((r) => r.id === selectedId) ?? null

  return (
    <div className="min-h-screen flex">
      <aside className="w-[380px] border-r border-border flex flex-col">
        <div className="px-5 py-4 border-b border-border">
          <div className="font-semibold text-[15px] flex items-center gap-2">
            <span className="text-accent">◆</span> Diffly
          </div>
          <div className="text-[11.5px] text-text-faint mt-0.5">AI pull request reviews</div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading && <p className="text-text-faint text-sm p-5">Loading…</p>}
          {requests?.length === 0 && (
            <p className="text-text-faint text-[12.5px] p-5 leading-relaxed">
              No review requests yet. Open a PR on a repo with the webhook configured, or check the
              README for the smee.io local-testing setup.
            </p>
          )}
          {requests?.map((r) => (
            <button
              key={r.id}
              onClick={() => setSelectedId(r.id)}
              className={`w-full text-left px-5 py-3.5 border-b border-border/60 hover:bg-card transition-colors ${
                selectedId === r.id ? 'bg-card' : ''
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className="text-[11.5px] text-text-faint truncate">{r.repo_full_name}</span>
                <StatusBadge status={r.status} />
              </div>
              <div className="text-[13.5px] font-medium leading-snug mb-1">
                #{r.pr_number} {r.pr_title}
              </div>
              <div className="text-[11px] text-text-faint">
                {r.author_login} · {timeAgo(r.created_at)}
              </div>
            </button>
          ))}
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        {selected ? (
          <ReviewPanel request={selected} />
        ) : (
          <div className="h-full flex items-center justify-center text-text-faint text-sm">
            Select a pull request to see its review.
          </div>
        )}
      </main>
    </div>
  )
}

function ReviewPanel({ request }: { request: ReviewRequest }) {
  const { data: review, isLoading } = useQuery({
    queryKey: ['review', request.id],
    queryFn: () => api.getReview(request.id),
    enabled: request.status === 'completed',
    retry: false,
  })

  return (
    <div className="max-w-[760px] mx-auto px-8 py-8">
      <div className="mb-1 text-[11.5px] text-text-faint">{request.repo_full_name}</div>
      <div className="flex items-center gap-3 mb-1">
        <h1 className="font-semibold text-xl">
          #{request.pr_number} {request.pr_title}
        </h1>
        <StatusBadge status={request.status} />
      </div>
      <a
        href={request.pr_url}
        target="_blank"
        rel="noreferrer"
        className="text-[12.5px] text-accent hover:underline"
      >
        View PR on GitHub →
      </a>

      <div className="mt-7 border-t border-border pt-6">
        {request.status === 'received' && (
          <p className="text-text-dim text-sm">Waiting to start review…</p>
        )}
        {request.status === 'processing' && (
          <p className="text-text-dim text-sm">Generating review — fetching diff, context, and calling the model…</p>
        )}
        {request.status === 'failed' && (
          <div className="bg-danger/10 border border-danger/30 rounded-lg p-4">
            <div className="text-danger text-sm font-medium mb-1">Review failed</div>
            <div className="text-[12.5px] text-text-dim">{request.error_message ?? 'Unknown error'}</div>
          </div>
        )}
        {request.status === 'completed' && (
          <>
            {isLoading && <p className="text-text-faint text-sm">Loading review…</p>}
            {review && (
              <>
                <div className="review-content text-[13.5px] text-text-dim mb-4">
                  <ReactMarkdown>{review.content}</ReactMarkdown>
                </div>
                <div className="flex items-center justify-between text-[11.5px] text-text-faint border-t border-border pt-3">
                  <span>
                    {review.model} · {review.input_tokens + review.output_tokens} tokens
                  </span>
                  {review.github_comment_url && (
                    <a href={review.github_comment_url} target="_blank" rel="noreferrer" className="text-accent hover:underline">
                      View comment on GitHub →
                    </a>
                  )}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
