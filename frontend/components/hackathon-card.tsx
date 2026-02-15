"use client"

import { useState } from "react"
import {
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Zap,
  TrendingUp,
  Shield,
  Lightbulb,
  Trophy,
  Rocket,
  AlertTriangle,
  Wrench,
  Target,
  ArrowUpRight,
  Radio,
  Flame,
  Users,
  Clock,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { Narrative, Idea } from "@/lib/mock-data"

function getVelocityColor(score: number) {
  if (score >= 4) return "text-emerald-400"
  if (score >= 2.5) return "text-amber-400"
  return "text-red-400"
}

function HackathonIdeaCard({ idea, index }: { idea: Idea; index: number }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={`overflow-hidden rounded-xl border transition-all duration-300 ${
        expanded
          ? "border-orange-500/30 bg-gradient-to-b from-orange-500/[0.04] to-transparent shadow-lg shadow-orange-500/5"
          : "border-border/40 bg-background/50 hover:border-orange-500/20 hover:bg-background/70"
      }`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-start gap-4 p-5 text-left"
      >
        <div
          className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl transition-colors ${
            expanded
              ? "bg-orange-500/20 ring-1 ring-orange-500/30"
              : "bg-orange-500/10 ring-1 ring-orange-500/20"
          }`}
        >
          <Rocket className={`h-5 w-5 ${expanded ? "text-orange-300" : "text-orange-400"}`} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-orange-500/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-orange-400 ring-1 ring-orange-500/20">
              Project #{index + 1}
            </span>
            {idea.supporting_signals.length > 0 && (
              <span className="rounded-md bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-medium text-emerald-400">
                {idea.supporting_signals.length} signals
              </span>
            )}
          </div>
          <h5 className="mt-1.5 text-sm font-semibold leading-snug text-foreground sm:text-base">
            {idea.title}
          </h5>
          {!expanded && (
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground line-clamp-2">
              {idea.description}
            </p>
          )}
        </div>
        <div
          className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg transition-colors ${
            expanded ? "bg-orange-500/10" : "bg-secondary/50"
          }`}
        >
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-orange-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="border-t border-border/20 px-5 pt-4 pb-2">
            <p className="text-sm leading-relaxed text-foreground/90">
              {idea.description}
            </p>
          </div>

          <div className="grid gap-3 px-5 py-4 sm:grid-cols-2">
            <div className="rounded-xl border border-red-500/15 bg-red-500/[0.04] p-4">
              <div className="mb-2.5 flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/15">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-red-400">
                  Problem
                </span>
              </div>
              <p className="text-sm leading-relaxed text-foreground/80">
                {idea.problem}
              </p>
            </div>

            <div className="rounded-xl border border-emerald-500/15 bg-emerald-500/[0.04] p-4">
              <div className="mb-2.5 flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/15">
                  <Wrench className="h-4 w-4 text-emerald-400" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  Solution
                </span>
              </div>
              <p className="text-sm leading-relaxed text-foreground/80">
                {idea.solution}
              </p>
            </div>

            <div className="rounded-xl border border-primary/15 bg-primary/[0.04] p-4">
              <div className="mb-2.5 flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/15">
                  <Rocket className="h-4 w-4 text-primary" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-primary">
                  Why Solana
                </span>
              </div>
              <p className="text-sm leading-relaxed text-foreground/80">
                {idea.why_solana}
              </p>
            </div>

            <div className="rounded-xl border border-violet-500/15 bg-violet-500/[0.04] p-4">
              <div className="mb-2.5 flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-violet-500/15">
                  <Target className="h-4 w-4 text-violet-400" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-violet-400">
                  Scale Potential
                </span>
              </div>
              <p className="text-sm leading-relaxed text-foreground/80">
                {idea.scale_potential}
              </p>
            </div>
          </div>

          {idea.supporting_signals.length > 0 && (
            <div className="border-t border-border/20 px-5 py-4">
              <div className="mb-3 flex items-center gap-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10">
                  <Radio className="h-3.5 w-3.5 text-primary" />
                </div>
                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Supporting Signals
                </span>
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold text-primary">
                  {idea.supporting_signals.length}
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {idea.supporting_signals.map((signal) => (
                  <span
                    key={signal}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-secondary/70 px-3 py-1.5 text-xs font-medium text-foreground/80 ring-1 ring-border/40 transition-colors hover:bg-secondary hover:text-foreground"
                  >
                    <ArrowUpRight className="h-3 w-3 text-primary/70" />
                    {signal}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function HackathonCard({ narrative }: { narrative: Narrative }) {
  const [expanded, setExpanded] = useState(false)
  const totalIdeas = narrative.ideas.length
  const totalEvidence = narrative.key_evidence.length

  return (
    <article className="group relative overflow-hidden rounded-xl border border-orange-500/20 bg-gradient-to-br from-card/80 via-card/60 to-orange-500/[0.02] backdrop-blur-sm transition-all hover:border-orange-500/30 hover:shadow-lg hover:shadow-orange-500/5">
      {/* Orange accent bar */}
      <div className="absolute left-0 top-0 h-full w-[3px] bg-gradient-to-b from-amber-400 via-orange-500 to-orange-500/30" />

      <div className="p-5 sm:p-6">
        {/* Top: Hackathon badge + confidence + velocity */}
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <span className="flex items-center gap-1.5 rounded-full bg-gradient-to-r from-amber-500/15 to-orange-500/15 px-3 py-1 text-xs font-bold text-orange-400 ring-1 ring-orange-500/25">
            <Trophy className="h-3.5 w-3.5" />
            Hackathon Track
          </span>
          <span
            className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ${
              narrative.confidence === "high"
                ? "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20"
                : narrative.confidence === "medium"
                  ? "bg-amber-500/10 text-amber-400 ring-amber-500/20"
                  : "bg-red-500/10 text-red-400 ring-red-500/20"
            }`}
          >
            <Shield className="h-3 w-3" />
            {narrative.confidence} confidence
          </span>
          <span className="flex items-center gap-1 rounded-full bg-secondary/50 px-2 py-0.5 text-[11px] font-medium text-muted-foreground ring-1 ring-border/40">
            <Zap className={`h-3 w-3 ${getVelocityColor(narrative.velocity_score)}`} />
            <span className={`font-bold ${getVelocityColor(narrative.velocity_score)}`}>
              {narrative.velocity_score.toFixed(1)}
            </span>
            velocity
          </span>
        </div>

        {/* Title */}
        <h3 className="mb-2 text-balance text-base font-bold leading-snug text-foreground sm:text-lg">
          {narrative.title}
        </h3>

        {/* Summary */}
        <p className="mb-4 text-pretty text-sm leading-relaxed text-muted-foreground">
          {narrative.summary}
        </p>

        {/* Tags */}
        <div className="mb-4 flex flex-wrap gap-1.5">
          {narrative.tags.map((tag) => (
            <Badge
              key={tag}
              variant="outline"
              className="border-orange-500/15 bg-orange-500/5 text-[11px] text-orange-300/80 hover:bg-orange-500/10"
            >
              {tag}
            </Badge>
          ))}
        </div>

        {/* Quick stats row */}
        <div className="mb-4 flex items-center gap-4 text-[11px] text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
            <span className="font-semibold text-foreground/80">{totalIdeas}</span> buildable ideas
          </span>
          <span className="flex items-center gap-1.5">
            <TrendingUp className="h-3.5 w-3.5 text-sky-400" />
            <span className="font-semibold text-foreground/80">{totalEvidence}</span> evidence points
          </span>
          <span className="flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5 text-primary" />
            <span className="font-semibold text-foreground/80">{narrative.supporting_source_names.length}</span> sources
          </span>
        </div>

        {/* Expand toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className={`flex w-full items-center justify-between rounded-xl px-4 py-3 transition-all duration-200 ${
            expanded
              ? "bg-orange-500/10 ring-1 ring-orange-500/20"
              : "bg-secondary/20 ring-1 ring-border/30 hover:bg-orange-500/5 hover:ring-orange-500/20"
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 rounded-lg bg-sky-500/10 px-2.5 py-1 ring-1 ring-sky-500/20">
              <TrendingUp className="h-3.5 w-3.5 text-sky-400" />
              <span className="text-xs font-semibold text-sky-400">{totalEvidence}</span>
              <span className="text-[11px] text-sky-400/70">Evidence</span>
            </div>
            <div className="flex items-center gap-1.5 rounded-lg bg-orange-500/10 px-2.5 py-1 ring-1 ring-orange-500/20">
              <Rocket className="h-3.5 w-3.5 text-orange-400" />
              <span className="text-xs font-semibold text-orange-400">{totalIdeas}</span>
              <span className="text-[11px] text-orange-400/70">Projects</span>
            </div>
            <span className="hidden text-[11px] text-muted-foreground/60 sm:inline">
              {expanded ? "Collapse details" : "View build ideas & evidence"}
            </span>
          </div>
          <div
            className={`flex h-7 w-7 items-center justify-center rounded-lg transition-colors ${
              expanded ? "bg-orange-500/15 text-orange-400" : "bg-secondary/60 text-muted-foreground"
            }`}
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </div>
        </button>

        {/* Expanded content */}
        {expanded && (
          <div className="mt-5 animate-in fade-in slide-in-from-top-2 duration-300">
            {/* Evidence section */}
            <div className="relative mb-6 rounded-2xl border border-sky-500/15 bg-gradient-to-b from-sky-500/[0.04] to-transparent p-5">
              <div className="absolute left-0 top-4 bottom-4 w-[3px] rounded-full bg-gradient-to-b from-sky-400 via-sky-400/50 to-transparent" />
              <div className="mb-4 flex items-center gap-3 pl-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15 ring-1 ring-sky-500/25">
                  <TrendingUp className="h-5 w-5 text-sky-400" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-foreground">Key Evidence</h4>
                  <p className="text-[11px] text-muted-foreground">
                    {totalEvidence} data points supporting this narrative
                  </p>
                </div>
              </div>
              <div className="space-y-2.5 pl-3">
                {narrative.key_evidence.map((ev, i) => (
                  <div
                    key={ev.signal_id}
                    className="rounded-xl border border-sky-500/10 bg-background/60 p-4 transition-colors hover:border-sky-500/20 hover:bg-background/80"
                  >
                    <div className="mb-2 flex items-start gap-2.5">
                      <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-md bg-sky-500/10 text-[10px] font-bold text-sky-400">
                        {i + 1}
                      </span>
                      <p className="text-sm leading-relaxed text-foreground/85">{ev.evidence}</p>
                    </div>
                    <div className="ml-7 flex items-center justify-between">
                      <div className="flex items-center gap-2 text-[11px]">
                        <span className="rounded-md bg-sky-500/10 px-2 py-0.5 font-semibold text-sky-400">
                          {ev.source_name}
                        </span>
                        <span className="text-muted-foreground">{ev.signal_title}</span>
                      </div>
                      <a
                        href={ev.content_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex flex-shrink-0 items-center gap-1 rounded-md bg-sky-500/5 px-2.5 py-1 text-[11px] font-medium text-sky-400/80 ring-1 ring-sky-500/15 transition-colors hover:bg-sky-500/10 hover:text-sky-300"
                      >
                        Source
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Build ideas section */}
            {narrative.ideas.length > 0 && (
              <div className="relative rounded-2xl border border-orange-500/15 bg-gradient-to-b from-orange-500/[0.04] to-transparent p-5">
                <div className="absolute left-0 top-4 bottom-4 w-[3px] rounded-full bg-gradient-to-b from-orange-400 via-amber-400/50 to-transparent" />
                <div className="mb-4 flex items-center gap-3 pl-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-500/15 ring-1 ring-orange-500/25">
                    <Rocket className="h-5 w-5 text-orange-400" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-foreground">Hackathon Project Ideas</h4>
                    <p className="text-[11px] text-muted-foreground">
                      {narrative.ideas.length} buildable projects ready for a hackathon submission
                    </p>
                  </div>
                </div>
                <div className="space-y-3 pl-3">
                  {narrative.ideas.map((idea, idx) => (
                    <HackathonIdeaCard key={idea.id} idea={idea} index={idx} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </article>
  )
}
