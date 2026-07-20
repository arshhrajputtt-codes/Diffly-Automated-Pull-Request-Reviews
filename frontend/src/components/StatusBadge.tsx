import type { ReviewStatus } from '../lib/types'

const STYLES: Record<ReviewStatus, string> = {
  received: 'bg-white/5 text-text-dim',
  queued: 'bg-white/5 text-text-dim',
  processing: 'bg-warn/15 text-warn',
  completed: 'bg-accent/15 text-accent',
  failed: 'bg-danger/15 text-danger',
}

const LABELS: Record<ReviewStatus, string> = {
  received: 'Received',
  queued: 'Queued',
  processing: 'Reviewing…',
  completed: 'Reviewed',
  failed: 'Failed',
}

export function StatusBadge({ status }: { status: ReviewStatus }) {
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${STYLES[status]}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {LABELS[status]}
    </span>
  )
}
