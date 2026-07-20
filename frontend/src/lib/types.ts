export type ReviewStatus = 'received' | 'queued' | 'processing' | 'completed' | 'failed'

export interface ReviewRequest {
  id: number
  repo_full_name: string
  pr_number: number
  pr_title: string
  pr_url: string
  head_sha: string
  base_ref: string
  action: string
  author_login: string
  status: ReviewStatus
  error_message: string | null
  created_at: string
}

export interface Review {
  id: number
  review_request_id: number
  content: string
  model: string
  input_tokens: number
  output_tokens: number
  github_comment_url: string | null
  created_at: string
}
