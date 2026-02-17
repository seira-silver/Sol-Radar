'use client'

import { SeiraMarkdown } from '@/components/seira-markdown'
import type { ChatMessage } from '@/lib/api-types'
import {
  ArrowUp,
  ExternalLink,
  Link2,
  Maximize2,
  Minimize2,
  Sparkles,
  Square,
  Trash2,
  X,
} from 'lucide-react'
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from 'react'

const URL_REGEX = /https?:\/\/[^\s<>)"']+/i

interface SeiraChatPanelProps {
  messages: ChatMessage[]
  isStreaming: boolean
  onSend: (content: string, url?: string | null) => void
  onStop: () => void
  onClear: () => void
  onClose: () => void
}

function TypingIndicator() {
  return (
    <div className='flex items-center gap-1 px-1 py-1'>
      <span className='h-1.5 w-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:0ms]' />
      <span className='h-1.5 w-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:150ms]' />
      <span className='h-1.5 w-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:300ms]' />
    </div>
  )
}

function SeiraAvatar({ size = 'sm' }: { size?: 'sm' | 'md' }) {
  const sizeClass = size === 'md' ? 'h-8 w-8' : 'h-6 w-6'
  const iconSize = size === 'md' ? 'h-4 w-4' : 'h-3 w-3'
  return (
    <div
      className={`${sizeClass} flex-shrink-0 flex items-center justify-center rounded-full bg-primary/15 ring-1 ring-primary/30`}
    >
      <Sparkles className={`${iconSize} text-primary`} />
    </div>
  )
}

export function SeiraChatPanel({
  messages,
  isStreaming,
  onSend,
  onStop,
  onClear,
  onClose,
}: SeiraChatPanelProps) {
  const [input, setInput] = useState('')
  const [detectedUrl, setDetectedUrl] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const bufferRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // After sending: scroll so last message is visible with buffer below, no auto-scroll during streaming
  useEffect(() => {
    const last = messages[messages.length - 1]
    if (last?.role === 'user' && bufferRef.current) {
      bufferRef.current.scrollIntoView({ block: 'end', behavior: 'smooth' })
    }
  }, [messages])

  // Focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus()
  }, [])

  // Detect URLs in input
  useEffect(() => {
    const match = input.match(URL_REGEX)
    setDetectedUrl(match ? match[0] : null)
  }, [input])

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`
    }
  }, [input])

  const handleSend = useCallback(() => {
    if (!input.trim() || isStreaming) return
    onSend(input, detectedUrl)
    setInput('')
    setDetectedUrl(null)
  }, [input, detectedUrl, isStreaming, onSend])

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const removeUrl = () => {
    if (detectedUrl) {
      setInput((prev) => prev.replace(detectedUrl, '').trim())
      setDetectedUrl(null)
    }
  }

  return (
    <div
      className={`fixed z-50 flex flex-col overflow-hidden rounded-2xl border border-border/50 bg-card/95 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-200 ${
        isExpanded
          ? 'inset-4 h-[calc(100vh-2rem)] w-[calc(100vw-2rem)]'
          : 'bottom-24 right-5 h-[600px] w-[420px] max-w-[calc(100vw-2.5rem)]'
      }`}
    >
      {/* Header */}
      <div className='flex items-center justify-between border-b border-border/50 px-4 py-3'>
        <div className='flex items-center gap-3'>
          <SeiraAvatar size='md' />
          <div className='flex flex-col'>
            <span className='text-sm font-semibold text-foreground'>Seira</span>
            <span className='text-[10px] font-medium text-muted-foreground'>
              Sol Radar AI Analyst
            </span>
          </div>
          <span className='ml-1 flex h-2 w-2'>
            <span className='absolute inline-flex h-2 w-2 animate-ping rounded-full bg-emerald-400 opacity-75' />
            <span className='relative inline-flex h-2 w-2 rounded-full bg-emerald-500' />
          </span>
        </div>
        <div className='flex items-center gap-1'>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className='rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary/80 hover:text-foreground'
            title={isExpanded ? 'Exit fullscreen' : 'Expand to fullscreen'}
          >
            {isExpanded ? (
              <Minimize2 className='h-4 w-4' />
            ) : (
              <Maximize2 className='h-4 w-4' />
            )}
          </button>
          <button
            onClick={onClear}
            className='rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary/80 hover:text-foreground'
            title='Clear history'
          >
            <Trash2 className='h-4 w-4' />
          </button>
          <button
            onClick={onClose}
            className='rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary/80 hover:text-foreground'
            title='Close'
          >
            <X className='h-4 w-4' />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className='flex-1 overflow-y-auto px-4 py-3 space-y-3 scrollbar-thin'>
        {messages.length === 0 && (
          <div className='flex h-full flex-col items-center justify-center text-center px-6'>
            <div className='mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20'>
              <Sparkles className='h-6 w-6 text-primary' />
            </div>
            <p className='text-sm font-medium text-foreground mb-1'>
              Hey, I&apos;m Seira
            </p>
            <p className='text-xs text-muted-foreground leading-relaxed'>
              Your Solana alpha analyst. Ask me about narratives, signals, or
              product ideas. Paste a link and I&apos;ll research it for you.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && <SeiraAvatar />}
            <div
              className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm ${
                msg.role === 'user'
                  ? 'rounded-br-sm bg-primary/15 text-foreground'
                  : 'rounded-bl-sm bg-secondary/80 text-foreground'
              }`}
            >
              {msg.role === 'assistant' ? (
                msg.content ? (
                  <div className='seira-prose text-[13px] leading-relaxed'>
                    <SeiraMarkdown content={msg.content} />
                  </div>
                ) : isStreaming && i === messages.length - 1 ? (
                  <TypingIndicator />
                ) : null
              ) : (
                <p className='whitespace-pre-wrap text-[13px] leading-relaxed'>
                  {msg.content}
                </p>
              )}
            </div>
          </div>
        ))}
        <div ref={bufferRef} className='min-h-32 flex-shrink-0' aria-hidden />
      </div>

      {/* URL detection pill */}
      {detectedUrl && (
        <div className='mx-4 mb-1 flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-1.5 ring-1 ring-primary/20'>
          <Link2 className='h-3.5 w-3.5 flex-shrink-0 text-primary' />
          <a
            href={detectedUrl}
            target='_blank'
            rel='noopener noreferrer'
            className='flex-1 truncate text-xs text-primary hover:underline'
          >
            {detectedUrl}
          </a>
          <ExternalLink className='h-3 w-3 flex-shrink-0 text-primary/60' />
          <button
            onClick={removeUrl}
            className='flex-shrink-0 rounded p-0.5 text-primary/60 hover:bg-primary/10 hover:text-primary'
          >
            <X className='h-3 w-3' />
          </button>
        </div>
      )}

      {/* Input */}
      <div className='border-t border-border/50 px-4 py-3'>
        <div className='flex items-end gap-2'>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Ask Seira anything... paste a link to study'
            rows={1}
            className='flex-1 resize-none rounded-xl border border-border/50 bg-secondary/50 px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/30 transition-colors'
            disabled={isStreaming}
          />
          {isStreaming ? (
            <button
              onClick={onStop}
              className='flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-destructive/80 text-destructive-foreground transition-colors hover:bg-destructive'
              title='Stop generating'
            >
              <Square className='h-4 w-4' />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className='flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed'
              title='Send message'
            >
              <ArrowUp className='h-4 w-4' />
            </button>
          )}
        </div>
        <p className='mt-1.5 text-center text-[10px] text-muted-foreground/50'>
          Seira cites Sol Radar narratives & signals. Shift+Enter for new line.
        </p>
      </div>
    </div>
  )
}
