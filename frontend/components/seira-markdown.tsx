"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { Components } from "react-markdown"

const components: Components = {
  a: ({ href, children, ...props }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary underline underline-offset-2 hover:text-primary/80 transition-colors"
      {...props}
    >
      {children}
    </a>
  ),
  h1: ({ children, ...props }) => (
    <h1 className="text-lg font-bold mt-4 mb-2 text-foreground" {...props}>
      {children}
    </h1>
  ),
  h2: ({ children, ...props }) => (
    <h2 className="text-base font-bold mt-3 mb-1.5 text-foreground" {...props}>
      {children}
    </h2>
  ),
  h3: ({ children, ...props }) => (
    <h3 className="text-sm font-semibold mt-2.5 mb-1 text-foreground" {...props}>
      {children}
    </h3>
  ),
  p: ({ children, ...props }) => (
    <p className="mb-2 last:mb-0 leading-relaxed" {...props}>
      {children}
    </p>
  ),
  ul: ({ children, ...props }) => (
    <ul className="mb-2 ml-4 list-disc space-y-0.5 marker:text-muted-foreground" {...props}>
      {children}
    </ul>
  ),
  ol: ({ children, ...props }) => (
    <ol className="mb-2 ml-4 list-decimal space-y-0.5 marker:text-muted-foreground" {...props}>
      {children}
    </ol>
  ),
  li: ({ children, ...props }) => (
    <li className="leading-relaxed" {...props}>
      {children}
    </li>
  ),
  strong: ({ children, ...props }) => (
    <strong className="font-semibold text-foreground" {...props}>
      {children}
    </strong>
  ),
  em: ({ children, ...props }) => (
    <em className="italic text-muted-foreground" {...props}>
      {children}
    </em>
  ),
  code: ({ children, className, ...props }) => {
    const isBlock = className?.includes("language-")
    if (isBlock) {
      return (
        <code
          className="block my-2 rounded-lg bg-background/80 px-3 py-2.5 font-mono text-xs text-foreground overflow-x-auto border border-border/50"
          {...props}
        >
          {children}
        </code>
      )
    }
    return (
      <code
        className="rounded bg-background/80 px-1.5 py-0.5 font-mono text-xs text-primary border border-border/50"
        {...props}
      >
        {children}
      </code>
    )
  },
  pre: ({ children, ...props }) => (
    <pre className="my-2 overflow-x-auto" {...props}>
      {children}
    </pre>
  ),
  blockquote: ({ children, ...props }) => (
    <blockquote
      className="my-2 border-l-2 border-primary/40 pl-3 text-muted-foreground italic"
      {...props}
    >
      {children}
    </blockquote>
  ),
  hr: ({ ...props }) => (
    <hr className="my-3 border-border/50" {...props} />
  ),
  table: ({ children, ...props }) => (
    <div className="my-2 overflow-x-auto rounded-lg border border-border/50">
      <table className="min-w-full text-xs" {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ children, ...props }) => (
    <th className="bg-secondary/50 px-3 py-1.5 text-left font-semibold text-foreground" {...props}>
      {children}
    </th>
  ),
  td: ({ children, ...props }) => (
    <td className="border-t border-border/30 px-3 py-1.5 text-muted-foreground" {...props}>
      {children}
    </td>
  ),
}

export function SeiraMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {content}
    </ReactMarkdown>
  )
}
