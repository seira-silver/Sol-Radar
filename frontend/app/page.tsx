"use client"

import { useState, useCallback, useMemo } from "react"
import { Navbar } from "@/components/navbar"
import type { TabType } from "@/components/navbar"
import { HeroSection } from "@/components/hero-section"
import { NarrativeCard } from "@/components/narrative-card"
import { SignalCard } from "@/components/signal-card"
import { HackathonCard } from "@/components/hackathon-card"
import { narrativesData, signalsData } from "@/lib/mock-data"
import { useInfiniteScroll } from "@/hooks/use-infinite-scroll"
import { Loader2, Trophy, Flame } from "lucide-react"

const ITEMS_PER_PAGE = 6

export default function Page() {
  const [activeTab, setActiveTab] = useState<TabType>("narratives")
  const [narrativeCount, setNarrativeCount] = useState(ITEMS_PER_PAGE)
  const [signalCount, setSignalCount] = useState(ITEMS_PER_PAGE)

  // Hackathon narratives: those with ideas and sorted by idea count * velocity
  const hackathonNarratives = useMemo(
    () =>
      [...narrativesData]
        .filter((n) => n.ideas.length > 0)
        .sort(
          (a, b) =>
            b.ideas.length * b.velocity_score - a.ideas.length * a.velocity_score
        ),
    []
  )

  const totalHackathonIdeas = useMemo(
    () => hackathonNarratives.reduce((sum, n) => sum + n.ideas.length, 0),
    [hackathonNarratives]
  )

  const visibleNarratives = useMemo(
    () => narrativesData.slice(0, narrativeCount),
    [narrativeCount]
  )
  const visibleSignals = useMemo(
    () => signalsData.slice(0, signalCount),
    [signalCount]
  )

  const hasMoreNarratives = narrativeCount < narrativesData.length
  const hasMoreSignals = signalCount < signalsData.length

  const loadMoreNarratives = useCallback(() => {
    setNarrativeCount((prev) => Math.min(prev + ITEMS_PER_PAGE, narrativesData.length))
  }, [])

  const loadMoreSignals = useCallback(() => {
    setSignalCount((prev) => Math.min(prev + ITEMS_PER_PAGE, signalsData.length))
  }, [])

  const { sentinelRef: narrativeSentinelRef } = useInfiniteScroll(
    loadMoreNarratives,
    hasMoreNarratives
  )
  const { sentinelRef: signalSentinelRef } = useInfiniteScroll(
    loadMoreSignals,
    hasMoreSignals
  )

  const tabHeaders: Record<TabType, { title: string; subtitle: string }> = {
    narratives: {
      title: `Active Narratives (${narrativesData.length})`,
      subtitle: "Sorted by velocity score",
    },
    signals: {
      title: `Recent Signals (${signalsData.length})`,
      subtitle: "Sorted by recency",
    },
    hackathon: {
      title: `Hackathon Tracks (${hackathonNarratives.length})`,
      subtitle: `${totalHackathonIdeas} buildable project ideas across all narratives`,
    },
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <HeroSection />

      <main className="mx-auto max-w-7xl px-4 pb-20 sm:px-6">
        {/* Tab content header */}
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">
            {tabHeaders[activeTab].title}
          </h2>
          <div className="text-xs text-muted-foreground">
            {tabHeaders[activeTab].subtitle}
          </div>
        </div>

        {/* Hackathon banner */}
        {activeTab === "hackathon" && (
          <div className="mb-6 flex items-center gap-4 rounded-xl border border-orange-500/20 bg-gradient-to-r from-orange-500/[0.06] via-amber-500/[0.04] to-transparent p-4">
            <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 ring-1 ring-orange-500/30">
              <Trophy className="h-6 w-6 text-orange-400" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-sm font-bold text-foreground">
                Hackathon Detection Mode
              </h3>
              <p className="text-xs leading-relaxed text-muted-foreground">
                Narratives ranked by buildability. Each track includes evidence-backed project ideas with problem/solution breakdowns ready for a hackathon submission.
              </p>
            </div>
            <div className="hidden items-center gap-1.5 rounded-lg bg-orange-500/10 px-3 py-1.5 ring-1 ring-orange-500/20 sm:flex">
              <Flame className="h-4 w-4 text-orange-400" />
              <span className="text-xs font-bold text-orange-400">{totalHackathonIdeas}</span>
              <span className="text-[11px] text-orange-400/70">Ideas</span>
            </div>
          </div>
        )}

        {/* Narratives tab */}
        {activeTab === "narratives" && (
          <div className="space-y-4">
            {visibleNarratives.map((narrative) => (
              <NarrativeCard key={narrative.id} narrative={narrative} />
            ))}
            {hasMoreNarratives && (
              <div ref={narrativeSentinelRef} className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
        )}

        {/* Signals tab */}
        {activeTab === "signals" && (
          <div className="space-y-4">
            {visibleSignals.map((signal) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
            {hasMoreSignals && (
              <div ref={signalSentinelRef} className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
        )}

        {/* Hackathon tab */}
        {activeTab === "hackathon" && (
          <div className="space-y-4">
            {hackathonNarratives.map((narrative) => (
              <HackathonCard key={narrative.id} narrative={narrative} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
