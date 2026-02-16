"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import type { ChatMessage } from "@/lib/api-types"
import { apiPostStream } from "@/lib/http"

const STORAGE_KEY = "seira-chat-history"
const MAX_STORED_MESSAGES = 100

function loadMessages(): ChatMessage[] {
  if (typeof window === "undefined") return []
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) return parsed.slice(-MAX_STORED_MESSAGES)
  } catch {
    /* ignore corrupt data */
  }
  return []
}

function saveMessages(messages: ChatMessage[]) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(messages.slice(-MAX_STORED_MESSAGES))
    )
  } catch {
    /* storage full — silently fail */
  }
}

export function useSeiraChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [hasUnread, setHasUnread] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const initializedRef = useRef(false)

  // Load from localStorage on mount (client only)
  useEffect(() => {
    if (!initializedRef.current) {
      initializedRef.current = true
      setMessages(loadMessages())
    }
  }, [])

  // Persist to localStorage on change
  useEffect(() => {
    if (initializedRef.current && messages.length > 0) {
      saveMessages(messages)
    }
  }, [messages])

  const sendMessage = useCallback(
    async (content: string, url?: string | null) => {
      if (isStreaming) return
      if (!content.trim()) return

      const userMsg: ChatMessage = { role: "user", content: content.trim() }
      const updatedMessages = [...messages, userMsg]
      setMessages(updatedMessages)

      const assistantMsg: ChatMessage = { role: "assistant", content: "" }
      setMessages((prev) => [...prev, assistantMsg])
      setIsStreaming(true)
      setHasUnread(true)

      const controller = new AbortController()
      abortRef.current = controller

      try {
        const apiMessages = updatedMessages.map((m) => ({
          role: m.role,
          content: m.content,
        }))

        const response = await apiPostStream(
          "/chat",
          { messages: apiMessages, url: url || null },
          { signal: controller.signal }
        )

        const reader = response.body?.getReader()
        if (!reader) throw new Error("No response stream")

        const decoder = new TextDecoder()
        let accumulated = ""

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const text = decoder.decode(value, { stream: true })
          const lines = text.split("\n")

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue
            const payload = line.slice(6).trim()

            if (payload === "[DONE]") break

            try {
              const parsed = JSON.parse(payload)
              if (parsed.content) {
                accumulated += parsed.content
                const current = accumulated
                setMessages((prev) => {
                  const next = [...prev]
                  const last = next[next.length - 1]
                  if (last && last.role === "assistant") {
                    next[next.length - 1] = { ...last, content: current }
                  }
                  return next
                })
              }
              if (parsed.error) {
                accumulated += `\n\n*Error: ${parsed.error}*`
                const current = accumulated
                setMessages((prev) => {
                  const next = [...prev]
                  const last = next[next.length - 1]
                  if (last && last.role === "assistant") {
                    next[next.length - 1] = { ...last, content: current }
                  }
                  return next
                })
              }
            } catch {
              /* skip malformed SSE lines */
            }
          }
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          // User cancelled — do nothing
        } else {
          const errorText =
            err instanceof Error ? err.message : "Something went wrong"
          setMessages((prev) => {
            const next = [...prev]
            const last = next[next.length - 1]
            if (last && last.role === "assistant") {
              next[next.length - 1] = {
                ...last,
                content: last.content || `*${errorText}*`,
              }
            }
            return next
          })
        }
      } finally {
        setIsStreaming(false)
        abortRef.current = null
      }
    },
    [messages, isStreaming]
  )

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  const clearHistory = useCallback(() => {
    setMessages([])
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      /* ignore */
    }
  }, [])

  const markRead = useCallback(() => {
    setHasUnread(false)
  }, [])

  return {
    messages,
    isStreaming,
    hasUnread,
    sendMessage,
    stopStreaming,
    clearHistory,
    markRead,
  }
}
