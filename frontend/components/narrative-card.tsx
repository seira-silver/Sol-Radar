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
  Globe,
  Rocket,
  AlertTriangle,
  Wrench,
  Target,
  ArrowUpRight,
  Radio,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { Narrative, Idea } from "@/lib/mock-data"

function getConfidenceConfig(confidence: string) {
  switch (confidence) {
    case "high":
      return {
        color: "bg-emerald-500/10 text-emerald-400 ring-emerald-500/20",
        icon: Shield,
        label: "High Confidence",
      }
    case "medium":
      return {
        color: "bg-amber-500/10 text-amber-400 ring-amber-500/20",
        icon: Shield,
        label: "Medium Confidence",
      }
    case "low":
      return {
        color: "bg-red-500/10 text-red-400 ring-red-500/20",
        icon: Shield,
        label: "Low Confidence",
      }
    default:
      return {
        color: "bg-muted text-muted-foreground ring-border",
        icon: Shield,
        label: "Unknown",
      }
  }
}

function getVelocityColor(score: number) {
  if (score >= 4) return "text-emerald-400"
  if (score >= 2.5) return "text-amber-400"
  return "text-red-400"
}

function getVelocityBarColor(score: number) {
  if (score >= 4) return "bg-emerald-500"
  if (score >= 2.5) return "bg-amber-500"
  return "bg-red-500"
}

function IdeaCard({ idea, index }: { idea: Idea; index: number }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={`overflow-hidden rounded-xl border transition-all duration-300 ${
        expanded
          ? "border-amber-500/30 bg-gradient-to-b from-amber-500/[0.03] to-transparent shadow-lg shadow-amber-500/5"
          : "border-border/40 bg-background/50 hover:border-amber-500/20 hover:bg-background/70"
      }`}
    >
      {/* Idea header - always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-start gap-4 p-5 text-left"
      >
        <div
          className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl transition-colors ${
            expanded
              ? "bg-amber-500/20 ring-1 ring-amber-500/30"
              : "bg-amber-500/10 ring-1 ring-amber-500/20"
          }`}
        >
          <Lightbulb className={`h-5 w-5 ${expanded ? "text-amber-300" : "text-amber-400"}`} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-secondary/60 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
              Idea #{index + 1}
            </span>
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
            expanded ? "bg-amber-500/10" : "bg-secondary/50"
          }`}
        >
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-amber-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Expanded idea details */}
      {expanded && (
        <div className="animate-in fade-in slide-in-from-top-2 duration-300">
          {/* Full description */}
          <div className="border-t border-border/20 px-5 pt-4 pb-2">
            <p className="text-sm leading-relaxed text-foreground/90">
              {idea.description}
            </p>
          </div>

          {/* Detail cards in 2-col grid */}
          <div className="grid gap-3 px-5 py-4 sm:grid-cols-2">
            {/* Problem */}
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

            {/* Solution */}
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

            {/* Why Solana */}
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

            {/* Scale Potential */}
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

          {/* Supporting signals */}
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

export function NarrativeCard({ narrative }: { narrative: Narrative }) {
  const [expanded, setExpanded] = useState(false)
  const confidence = getConfidenceConfig(narrative.confidence)
  const ConfidenceIcon = confidence.icon

  return (
    <article className="group relative overflow-hidden rounded-xl border border-border/50 bg-card/60 backdrop-blur-sm transition-all hover:border-border hover:bg-card/80 hover:shadow-lg hover:shadow-primary/5">
      {/* Rank indicator glow */}
      {narrative.rank <= 3 && (
        <div className="absolute left-0 top-0 h-full w-[2px] bg-gradient-to-b from-primary via-primary/50 to-transparent" />
      )}

      <div className="p-5 sm:p-6">
        {/* Top row: Rank + Title + Confidence */}
        <div className="mb-3 flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-secondary text-xs font-bold text-muted-foreground ring-1 ring-border/50">
              #{narrative.rank}
            </div>
            <h3 className="text-balance text-base font-semibold leading-snug text-foreground sm:text-lg">
              {narrative.title}
            </h3>
          </div>
          <div
            className={`flex flex-shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${confidence.color}`}
          >
            <ConfidenceIcon className="h-3 w-3" />
            <span className="hidden sm:inline">{confidence.label}</span>
            <span className="capitalize sm:hidden">{narrative.confidence}</span>
          </div>
        </div>

        {/* Summary */}
        <p className="mb-4 text-pretty text-sm leading-relaxed text-muted-foreground">
          {narrative.summary}
        </p>

        {/* Velocity + Tags + Sources */}
        <div className="mb-4 flex flex-wrap items-center gap-3">
          {/* Velocity */}
          <div className="flex items-center gap-2 rounded-lg bg-secondary/50 px-3 py-1.5 ring-1 ring-border/50">
            <Zap
              className={`h-3.5 w-3.5 ${getVelocityColor(narrative.velocity_score)}`}
            />
            <div className="flex items-center gap-2">
              <span
                className={`text-sm font-bold ${getVelocityColor(narrative.velocity_score)}`}
              >
                {narrative.velocity_score.toFixed(1)}
              </span>
              <div className="h-1.5 w-16 overflow-hidden rounded-full bg-secondary">
                <div
                  className={`h-full rounded-full ${getVelocityBarColor(narrative.velocity_score)} transition-all`}
                  style={{
                    width: `${Math.min(100, (narrative.velocity_score / 5.5) * 100)}%`,
                  }}
                />
              </div>
            </div>
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
              velocity
            </span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1.5">
            {narrative.tags.map((tag) => (
              <Badge
                key={tag}
                variant="outline"
                className="border-border/50 bg-secondary/30 text-[11px] text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
              >
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Sources row */}
        {narrative.supporting_source_names.length > 0 && (
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              <Globe className="h-3 w-3" />
              Sources
            </span>
            {narrative.supporting_source_names.map((source) => (
              <span
                key={source}
                className="rounded-md bg-primary/5 px-2 py-0.5 text-[11px] font-medium text-primary/80 ring-1 ring-primary/10"
              >
                {source}
              </span>
            ))}
          </div>
        )}

        {/* Expandable Evidence + Ideas toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className={`flex w-full items-center justify-between rounded-xl px-4 py-3 transition-all duration-200 ${
            expanded
              ? "bg-secondary/50 ring-1 ring-border/50"
              : "bg-secondary/20 ring-1 ring-border/30 hover:bg-secondary/40 hover:ring-border/50"
          }`}
        >
          <div className="flex items-center gap-3">
            {/* Evidence pill */}
            <div className="flex items-center gap-1.5 rounded-lg bg-sky-500/10 px-2.5 py-1 ring-1 ring-sky-500/20">
              <TrendingUp className="h-3.5 w-3.5 text-sky-400" />
              <span className="text-xs font-semibold text-sky-400">
                {narrative.key_evidence.length}
              </span>
              <span className="text-[11px] text-sky-400/70">Evidence</span>
            </div>

            {/* Ideas pill */}
            {narrative.ideas.length > 0 && (
              <div className="flex items-center gap-1.5 rounded-lg bg-amber-500/10 px-2.5 py-1 ring-1 ring-amber-500/20">
                <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
                <span className="text-xs font-semibold text-amber-400">
                  {narrative.ideas.length}
                </span>
                <span className="text-[11px] text-amber-400/70">Ideas</span>
              </div>
            )}

            {/* Divider + label */}
            <span className="hidden text-[11px] text-muted-foreground/60 sm:inline">
              {expanded ? "Collapse details" : "Expand details"}
            </span>
          </div>

          <div
            className={`flex h-7 w-7 items-center justify-center rounded-lg transition-colors ${
              expanded
                ? "bg-primary/10 text-primary"
                : "bg-secondary/60 text-muted-foreground"
            }`}
          >
            {expanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </div>
        </button>

        {expanded && (
          <div className="mt-5 animate-in fade-in slide-in-from-top-2 duration-300">
            {/* Confidence Reasoning */}
            <div className="mb-6 rounded-lg border border-border/30 bg-secondary/10 p-3.5">
              <span className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                <Shield className="h-3 w-3" />
                Confidence Reasoning
              </span>
              <p className="text-sm leading-relaxed text-foreground/70">
                {narrative.confidence_reasoning}
              </p>
            </div>

            {/* ========= KEY EVIDENCE SECTION ========= */}
            <div className="relative mb-8 rounded-2xl border border-sky-500/15 bg-gradient-to-b from-sky-500/[0.04] to-transparent p-5">
              {/* Section accent line */}
              <div className="absolute left-0 top-4 bottom-4 w-[3px] rounded-full bg-gradient-to-b from-sky-400 via-sky-400/50 to-transparent" />

              <div className="mb-4 flex items-center gap-3 pl-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15 ring-1 ring-sky-500/25">
                  <TrendingUp className="h-4.5 w-4.5 text-sky-400" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-foreground">
                    Key Evidence
                  </h4>
                  <p className="text-[11px] text-muted-foreground">
                    {narrative.key_evidence.length} supporting data points from verified sources
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
                      <p className="text-sm leading-relaxed text-foreground/85">
                        {ev.evidence}
                      </p>
                    </div>
                    <div className="ml-7 flex items-center justify-between">
                      <div className="flex items-center gap-2 text-[11px]">
                        <span className="rounded-md bg-sky-500/10 px-2 py-0.5 font-semibold text-sky-400">
                          {ev.source_name}
                        </span>
                        <span className="text-muted-foreground">
                          {ev.signal_title}
                        </span>
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

            {/* ========= BUILD IDEAS SECTION ========= */}
            {narrative.ideas.length > 0 && (
              <div className="relative rounded-2xl border border-amber-500/15 bg-gradient-to-b from-amber-500/[0.04] to-transparent p-5">
                {/* Section accent line */}
                <div className="absolute left-0 top-4 bottom-4 w-[3px] rounded-full bg-gradient-to-b from-amber-400 via-amber-400/50 to-transparent" />

                <div className="mb-4 flex items-center gap-3 pl-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15 ring-1 ring-amber-500/25">
                    <Lightbulb className="h-4.5 w-4.5 text-amber-400" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-foreground">
                      Build Ideas
                    </h4>
                    <p className="text-[11px] text-muted-foreground">
                      {narrative.ideas.length} actionable project concepts derived from this narrative
                    </p>
                  </div>
                </div>

                <div className="space-y-3 pl-3">
                  {narrative.ideas.map((idea, idx) => (
                    <IdeaCard key={idea.id} idea={idea} index={idx} />
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
