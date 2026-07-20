import type { Review, ReviewRequest } from './types'

const API_URL = import.meta.env.VITE_DIFFLY_API_URL ?? 'http://localhost:8010'

class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`)
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new ApiError(response.status, body.detail ?? 'Request failed')
  }
  return response.json() as Promise<T>
}

export const api = {
  listReviewRequests: () => request<ReviewRequest[]>('/review-requests'),
  getReviewRequest: (id: number) => request<ReviewRequest>(`/review-requests/${id}`),
  getReview: (reviewRequestId: number) => request<Review>(`/review-requests/${reviewRequestId}/review`),
}

export { ApiError }
