"use client"

import { statsData } from "@/lib/mock-data"
import {
  Radar,
  Activity,
  Lightbulb,
  Zap,
  Users,
  Globe,
} from "lucide-react"

function formatTime(isoString: string) {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHrs = Math.floor(diffMins / 60)

  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHrs < 24) return `${diffHrs}h ago`
  return `${Math.floor(diffHrs / 24)}d ago`
}

function formatNextSynthesis(isoString: string) {
  const date = new Date(isoString)
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

const stats = [
  {
    label: "Active Narratives",
    value: statsData.active_narratives_count,
    icon: Radar,
    color: "text-primary",
    bgColor: "bg-primary/10",
    ringColor: "ring-primary/20",
  },
  {
    label: "Signals Detected",
    value: statsData.total_signals_count,
    icon: Activity,
    color: "text-chart-2",
    bgColor: "bg-chart-2/10",
    ringColor: "ring-chart-2/20",
  },
  {
    label: "Build Ideas",
    value: statsData.total_ideas_count,
    icon: Lightbulb,
    color: "text-warning",
    bgColor: "bg-warning/10",
    ringColor: "ring-warning/20",
  },
  {
    label: "Avg Velocity",
    value: statsData.avg_velocity_score.toFixed(1),
    icon: Zap,
    color: "text-chart-5",
    bgColor: "bg-chart-5/10",
    ringColor: "ring-chart-5/20",
  },
  {
    label: "Active Builders",
    value: statsData.active_builders,
    icon: Users,
    color: "text-chart-4",
    bgColor: "bg-chart-4/10",
    ringColor: "ring-chart-4/20",
  },
  {
    label: "Sources Scraped",
    value: statsData.sources_scraped_count,
    icon: Globe,
    color: "text-primary",
    bgColor: "bg-primary/10",
    ringColor: "ring-primary/20",
  },
]

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Glowing background orbs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/4 top-0 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-primary/8 blur-[120px] animate-pulse-glow" />
        <div className="absolute right-1/4 top-10 h-[400px] w-[400px] translate-x-1/2 rounded-full bg-chart-2/6 blur-[100px] animate-pulse-glow" style={{ animationDelay: "2s" }} />
        <div className="absolute bottom-0 left-1/2 h-[300px] w-[600px] -translate-x-1/2 rounded-full bg-chart-4/5 blur-[80px] animate-pulse-glow" style={{ animationDelay: "3s" }} />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 pb-8 pt-12 sm:px-6 sm:pt-16">
        {/* Header */}
        <div className="mb-10 flex flex-col items-center text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-xs font-medium text-primary ring-1 ring-primary/20">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
            </span>
            Live - Updated {formatTime(statsData.last_web_scrape_time)}
          </div>
          <h1 className="text-balance text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Solana Narrative
            <span className="bg-gradient-to-r from-primary via-chart-2 to-primary bg-clip-text text-transparent"> Intelligence</span>
          </h1>
          <p className="mt-3 max-w-2xl text-pretty text-sm text-muted-foreground sm:text-base">
            Detecting emerging narratives and early signals within the Solana ecosystem.
            Next synthesis: {formatNextSynthesis(statsData.next_synthesis_time)}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="group relative flex flex-col items-center gap-2 rounded-xl border border-border/50 bg-card/50 p-4 backdrop-blur-sm transition-all hover:border-border hover:bg-card/80"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.bgColor} ring-1 ${stat.ringColor} transition-transform group-hover:scale-110`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <span className={`text-2xl font-bold ${stat.color}`}>
                {stat.value}
              </span>
              <span className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                {stat.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
