"use client"

import {
  ExternalLink,
  MessageSquare,
  Code2,
  AlertTriangle,
  Globe,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { Signal } from "@/lib/api-types"

function getSignalTypeConfig(type: string) {
  switch (type) {
    case "social":
      return {
        icon: MessageSquare,
        color: "text-chart-2",
        bgColor: "bg-chart-2/10",
        label: "Social",
      }
    case "developer":
      return {
        icon: Code2,
        color: "text-primary",
        bgColor: "bg-primary/10",
        label: "Developer",
      }
    case "other":
      return {
        icon: AlertTriangle,
        color: "text-warning",
        bgColor: "bg-warning/10",
        label: "Other",
      }
    default:
      return {
        icon: Globe,
        color: "text-muted-foreground",
        bgColor: "bg-muted",
        label: type,
      }
  }
}

function getNoveltyConfig(novelty: string) {
  switch (novelty) {
    case "high":
      return "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20"
    case "medium":
      return "bg-amber-500/10 text-amber-400 ring-amber-500/20"
    case "low":
      return "bg-muted text-muted-foreground ring-border/50"
    default:
      return "bg-muted text-muted-foreground ring-border/50"
  }
}

function timeAgo(isoString: string) {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHrs = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHrs / 24)

  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHrs < 24) return `${diffHrs}h ago`
  return `${diffDays}d ago`
}

export function SignalCard({ signal }: { signal: Signal }) {
  const typeConfig = getSignalTypeConfig(signal.signal_type)
  const TypeIcon = typeConfig.icon

  return (
    <article className="group relative overflow-hidden rounded-xl border border-border/50 bg-card/60 backdrop-blur-sm transition-all hover:border-border hover:bg-card/80 hover:shadow-lg hover:shadow-primary/5">
      <div className="p-5 sm:p-6">
        {/* Header: Type icon + Title + Novelty */}
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg ${typeConfig.bgColor}`}>
              <TypeIcon className={`h-4.5 w-4.5 ${typeConfig.color}`} />
            </div>
            <div className="flex flex-col gap-1">
              <h3 className="text-balance text-base font-semibold leading-snug text-foreground">
                {signal.signal_title}
              </h3>
              <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                <span className="font-medium">{signal.data_source_name}</span>
                <span className="text-border">|</span>
                <span>{timeAgo(signal.created_at)}</span>
              </div>
            </div>
          </div>
          <div className={`flex flex-shrink-0 items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-medium ring-1 ${getNoveltyConfig(signal.novelty)}`}>
            <span className="capitalize">{signal.novelty}</span>
            <span className="text-[10px] opacity-60">novelty</span>
          </div>
        </div>

        {/* Description */}
        <p className="mb-3 text-pretty text-sm leading-relaxed text-muted-foreground">
          {signal.description}
        </p>

        {/* Evidence quote */}
        <div className="mb-4 rounded-lg border-l-2 border-primary/30 bg-secondary/20 px-3 py-2">
          <p className="font-mono text-xs leading-relaxed text-foreground/70">
            {signal.evidence}
          </p>
        </div>

        {/* Bottom row: Tags + Projects + Source link */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge
              variant="outline"
              className="border-border/50 bg-secondary/30 text-[11px] text-muted-foreground"
            >
              {typeConfig.label}
            </Badge>
            {signal.tags.map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="border-border/50 bg-secondary/30 text-[11px] text-muted-foreground"
              >
                {tag}
              </Badge>
            ))}
            {signal.related_projects.map((project) => (
              <Badge
                key={project}
                className="border-primary/20 bg-primary/10 text-[11px] text-primary"
              >
                {project}
              </Badge>
            ))}
          </div>

          <a
            href={signal.content_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground transition-colors hover:text-primary"
          >
            Source
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>
    </article>
  )
}
