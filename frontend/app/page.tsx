"use client"

import { useEffect, useMemo, useRef, useState, useCallback } from "react"
import { Navbar } from "@/components/navbar"
import type { TabType } from "@/components/navbar"
import { HeroSection } from "@/components/hero-section"
import { NarrativeCard } from "@/components/narrative-card"
import { SignalCard } from "@/components/signal-card"
import { HackathonCard } from "@/components/hackathon-card"
import type { Narrative, Signal, Stats } from "@/lib/api-types"
import {
  getLanding,
  getNarrativeDetail,
  listHackathonNarratives,
  listSignals,
} from "@/lib/api"
import { useInfiniteScroll } from "@/hooks/use-infinite-scroll"
import { Loader2, Trophy, Flame } from "lucide-react"

const ITEMS_PER_PAGE = 6

export default function Page() {
  const [activeTab, setActiveTab] = useState<TabType>("narratives")
  const [stats, setStats] = useState<Stats | null>(null)

  // --- Narratives ---
  const [narratives, setNarratives] = useState<Narrative[]>([])
  const [narrativesTotal, setNarrativesTotal] = useState(0)
  const [narrativesLoading, setNarrativesLoading] = useState(false)
  const narrativesLoadingRef = useRef(false)
  const narrativesFetchedRef = useRef(false)

  // --- Signals ---
  const [signals, setSignals] = useState<Signal[]>([])
  const [signalsTotal, setSignalsTotal] = useState(0)
  const [signalsLoading, setSignalsLoading] = useState(false)
  const signalsLoadingRef = useRef(false)
  const signalsFetchedRef = useRef(false)

  // --- Hackathons ---
  const [hackathons, setHackathons] = useState<Narrative[]>([])
  const [hackathonsTotal, setHackathonsTotal] = useState(0)
  const [hackathonsLoading, setHackathonsLoading] = useState(false)
  const hackathonsLoadingRef = useRef(false)
  const hackathonsFetchedRef = useRef(false)

  // Offset refs — track current pagination cursor without reading state in callbacks
  const narrativesOffsetRef = useRef(0)
  const signalsOffsetRef = useRef(0)
  const hackathonsOffsetRef = useRef(0)

  const hasMoreNarratives = narratives.length < narrativesTotal
  const hasMoreSignals = signals.length < signalsTotal
  const hasMoreHackathons = hackathons.length < hackathonsTotal

  const totalHackathonIdeas = useMemo(
    () =>
      hackathons.reduce(
        (sum, n) => sum + (n.ideas?.length ?? n.idea_count ?? 0),
        0
      ),
    [hackathons]
  )

  // ─── Hydrate hackathon ideas from detail endpoint ──────────────
  // Returns a promise so callers can chain it into the loading lifecycle.

  function hydrateMissingIdeas(page: Narrative[]): Promise<void> {
    const needsDetail = page.filter(
      (n) => (n.idea_count ?? 0) > 0 && (!n.ideas || n.ideas.length === 0)
    )
    if (needsDetail.length === 0) return Promise.resolve()

    return Promise.all(
      needsDetail.map((n) =>
        getNarrativeDetail({ id: n.id }).catch(() => null)
      )
    ).then((details) => {
      setHackathons((prev) =>
        prev.map((n) => {
          const d = details.find((x) => x && x.id === n.id)
          return d ? { ...n, ideas: d.ideas } : n
        })
      )
    })
  }

  // ─── Narratives (via /landing) ─────────────────────────────────

  useEffect(() => {
    if (narrativesFetchedRef.current) return
    narrativesFetchedRef.current = true

    const ac = new AbortController()
    setNarrativesLoading(true)
    narrativesLoadingRef.current = true

    getLanding({
      narratives_limit: ITEMS_PER_PAGE,
      narratives_offset: 0,
      signal: ac.signal,
    })
      .then((data) => {
        setStats(data.stats)
        setNarratives(data.narratives.narratives)
        setNarrativesTotal(data.narratives.total)
        narrativesOffsetRef.current = data.narratives.narratives.length
      })
      .catch((err) => {
        if (err?.name !== "AbortError") console.error("Landing fetch failed:", err)
      })
      .finally(() => {
        setNarrativesLoading(false)
        narrativesLoadingRef.current = false
      })

    return () => ac.abort()
  }, [])

  const loadMoreNarratives = useCallback(() => {
    if (narrativesLoadingRef.current) return
    narrativesLoadingRef.current = true
    setNarrativesLoading(true)

    const offset = narrativesOffsetRef.current

    getLanding({
      narratives_limit: ITEMS_PER_PAGE,
      narratives_offset: offset,
    })
      .then((data) => {
        const page = data.narratives.narratives
        setStats(data.stats)
        setNarratives((curr) => [...curr, ...page])
        setNarrativesTotal(data.narratives.total)
        narrativesOffsetRef.current = offset + page.length
      })
      .catch((err) => {
        console.error("Load more narratives failed:", err)
      })
      .finally(() => {
        setNarrativesLoading(false)
        narrativesLoadingRef.current = false
      })
  }, [])

  // ─── Signals (via /signals) ────────────────────────────────────

  useEffect(() => {
    if (activeTab !== "signals") return
    if (signalsFetchedRef.current) return
    signalsFetchedRef.current = true

    const ac = new AbortController()
    setSignalsLoading(true)
    signalsLoadingRef.current = true

    listSignals({ limit: ITEMS_PER_PAGE, offset: 0, signal: ac.signal })
      .then((data) => {
        setSignals(data.signals)
        setSignalsTotal(data.total)
        signalsOffsetRef.current = data.signals.length
      })
      .catch((err) => {
        if (err?.name !== "AbortError") console.error("Signals fetch failed:", err)
      })
      .finally(() => {
        setSignalsLoading(false)
        signalsLoadingRef.current = false
      })

    return () => ac.abort()
  }, [activeTab])

  const loadMoreSignals = useCallback(() => {
    if (signalsLoadingRef.current) return
    signalsLoadingRef.current = true
    setSignalsLoading(true)

    const offset = signalsOffsetRef.current

    listSignals({ limit: ITEMS_PER_PAGE, offset })
      .then((data) => {
        setSignals((curr) => [...curr, ...data.signals])
        setSignalsTotal(data.total)
        signalsOffsetRef.current = offset + data.signals.length
      })
      .catch((err) => {
        console.error("Load more signals failed:", err)
      })
      .finally(() => {
        setSignalsLoading(false)
        signalsLoadingRef.current = false
      })
  }, [])

  // ─── Hackathons (via /narratives/hackathons) ───────────────────

  useEffect(() => {
    if (activeTab !== "hackathon") return
    if (hackathonsFetchedRef.current) return
    hackathonsFetchedRef.current = true

    const ac = new AbortController()
    setHackathonsLoading(true)
    hackathonsLoadingRef.current = true

    listHackathonNarratives({ limit: ITEMS_PER_PAGE, offset: 0, signal: ac.signal })
      .then((data) => {
        setHackathons(data.narratives)
        setHackathonsTotal(data.total)
        hackathonsOffsetRef.current = data.narratives.length
        // Chain hydration so .finally() waits for it to complete
        return hydrateMissingIdeas(data.narratives)
      })
      .catch((err) => {
        if (err?.name !== "AbortError") console.error("Hackathons fetch failed:", err)
      })
      .finally(() => {
        setHackathonsLoading(false)
        hackathonsLoadingRef.current = false
      })

    return () => ac.abort()
  }, [activeTab])

  const loadMoreHackathons = useCallback(() => {
    if (hackathonsLoadingRef.current) return
    hackathonsLoadingRef.current = true
    setHackathonsLoading(true)

    const offset = hackathonsOffsetRef.current

    listHackathonNarratives({ limit: ITEMS_PER_PAGE, offset })
      .then((data) => {
        setHackathons((curr) => [...curr, ...data.narratives])
        setHackathonsTotal(data.total)
        hackathonsOffsetRef.current = offset + data.narratives.length
        // Chain hydration so .finally() waits for it to complete
        return hydrateMissingIdeas(data.narratives)
      })
      .catch((err) => {
        console.error("Load more hackathons failed:", err)
      })
      .finally(() => {
        setHackathonsLoading(false)
        hackathonsLoadingRef.current = false
      })
  }, [])

  // ─── Infinite scroll hooks ─────────────────────────────────────

  const { sentinelRef: narrativeSentinelRef } = useInfiniteScroll(
    loadMoreNarratives,
    hasMoreNarratives && !narrativesLoading
  )
  const { sentinelRef: signalSentinelRef } = useInfiniteScroll(
    loadMoreSignals,
    hasMoreSignals && !signalsLoading
  )
  const { sentinelRef: hackathonSentinelRef } = useInfiniteScroll(
    loadMoreHackathons,
    hasMoreHackathons && !hackathonsLoading
  )

  // ─── Tab headers ───────────────────────────────────────────────

  const tabHeaders: Record<TabType, { title: string; subtitle: string }> = {
    narratives: {
      title: `Active Narratives (${narrativesTotal})`,
      subtitle: "Sorted by velocity score",
    },
    signals: {
      title: `Recent Signals (${signalsTotal})`,
      subtitle: "Sorted by recency",
    },
    hackathon: {
      title: `Hackathon Tracks (${hackathonsTotal})`,
      subtitle: `${totalHackathonIdeas} buildable project ideas across all narratives`,
    },
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <HeroSection statsData={stats} />

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
            {narratives.map((narrative) => (
              <NarrativeCard key={narrative.id} narrative={narrative} />
            ))}
            {(hasMoreNarratives || narrativesLoading) && (
              <div ref={narrativeSentinelRef} className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
        )}

        {/* Signals tab */}
        {activeTab === "signals" && (
          <div className="space-y-4">
            {signals.map((signal) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
            {(hasMoreSignals || signalsLoading) && (
              <div ref={signalSentinelRef} className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
        )}

        {/* Hackathon tab */}
        {activeTab === "hackathon" && (
          <div className="space-y-4">
            {hackathons.map((narrative) => (
              <HackathonCard key={narrative.id} narrative={narrative} />
            ))}
            {(hasMoreHackathons || hackathonsLoading) && (
              <div ref={hackathonSentinelRef} className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
