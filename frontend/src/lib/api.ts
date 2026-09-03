const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  body: unknown

  constructor(status: number, body: unknown) {
    const detail = extractDetailMessage(body)
    super(detail ?? `Request failed with status ${status}`)
    this.status = status
    this.body = body
  }
}

function extractDetailMessage(body: unknown): string | undefined {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
  }
  return undefined
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const text = await response.text()
  const data = text ? JSON.parse(text) : undefined

  if (!response.ok) {
    throw new ApiError(response.status, data)
  }

  return data as T
}
