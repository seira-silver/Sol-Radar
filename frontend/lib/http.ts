import { API_URL } from "@/lib/constants"

type QueryValue = string | number | boolean | null | undefined

function buildUrl(path: string, query?: Record<string, QueryValue>) {
  const base = (API_URL || "").replace(/\/+$/, "")
  const fullPath = path.startsWith("/") ? path : `/${path}`

  if (!base) {
    throw new Error("NEXT_PUBLIC_API_URL is not set")
  }

  const url = new URL(`${base}${fullPath}`)
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null) continue
      url.searchParams.set(k, String(v))
    }
  }
  return url.toString()
}

export class HttpError extends Error {
  status: number
  body?: unknown

  constructor(message: string, status: number, body?: unknown) {
    super(message)
    this.name = "HttpError"
    this.status = status
    this.body = body
  }
}

export async function apiGet<T>(
  path: string,
  opts?: { query?: Record<string, QueryValue>; signal?: AbortSignal }
): Promise<T> {
  const url = buildUrl(path, opts?.query)
  const res = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal: opts?.signal,
    cache: "no-store",
  })

  if (!res.ok) {
    let body: unknown = undefined
    try {
      body = await res.json()
    } catch {
      try {
        body = await res.text()
      } catch {
        body = undefined
      }
    }
    throw new HttpError(`GET ${path} failed (${res.status})`, res.status, body)
  }

  return (await res.json()) as T
}

