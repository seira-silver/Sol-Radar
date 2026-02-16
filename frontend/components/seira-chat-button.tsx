"use client"

import { useState, useCallback } from "react"
import { Sparkles, MessageCircle } from "lucide-react"
import { useSeiraChat } from "@/hooks/use-seira-chat"
import { SeiraChatPanel } from "@/components/seira-chat-panel"

export function SeiraChatButton() {
  const [isOpen, setIsOpen] = useState(false)
  const {
    messages,
    isStreaming,
    hasUnread,
    sendMessage,
    stopStreaming,
    clearHistory,
    markRead,
  } = useSeiraChat()

  const toggleOpen = useCallback(() => {
    setIsOpen((prev) => {
      const next = !prev
      if (next) markRead()
      return next
    })
  }, [markRead])

  const handleClose = useCallback(() => {
    setIsOpen(false)
  }, [])

  return (
    <>
      {/* Chat panel */}
      {isOpen && (
        <SeiraChatPanel
          messages={messages}
          isStreaming={isStreaming}
          onSend={sendMessage}
          onStop={stopStreaming}
          onClear={clearHistory}
          onClose={handleClose}
        />
      )}

      {/* Floating action button */}
      <button
        onClick={toggleOpen}
        className="fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 hover:scale-105 active:scale-95"
        title={isOpen ? "Close Seira" : "Chat with Seira"}
        aria-label={isOpen ? "Close Seira chat" : "Open Seira chat"}
      >
        {isOpen ? (
          <MessageCircle className="h-6 w-6 text-primary-foreground" />
        ) : (
          <Sparkles className="h-6 w-6 text-primary-foreground" />
        )}

        {/* Unread indicator */}
        {!isOpen && hasUnread && (
          <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-chart-5 opacity-75" />
            <span className="relative inline-flex h-3.5 w-3.5 rounded-full bg-chart-5" />
          </span>
        )}

        {/* Glow ring */}
        <div className="absolute inset-0 rounded-full bg-primary/10 animate-pulse-glow pointer-events-none" />
      </button>
    </>
  )
}
