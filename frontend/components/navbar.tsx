"use client"

import { Radar, Activity, Trophy } from "lucide-react"

export type TabType = "narratives" | "signals" | "hackathon"

interface NavbarProps {
  activeTab: TabType
  onTabChange: (tab: TabType) => void
}

const tabs: { id: TabType; label: string; icon: typeof Radar }[] = [
  { id: "narratives", label: "Narratives", icon: Radar },
  { id: "signals", label: "Signals", icon: Activity },
  { id: "hackathon", label: "Hackathon", icon: Trophy },
]

export function Navbar({ activeTab, onTabChange }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 ring-1 ring-primary/20">
            <Radar className="h-5 w-5 text-primary" />
            <div className="absolute inset-0 rounded-lg bg-primary/5 animate-pulse-glow" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-bold tracking-tight text-foreground">
              Sol Radar
            </span>
            <span className="text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
              Narrative Intelligence
            </span>
          </div>
        </div>

        <nav className="flex items-center gap-1 rounded-lg bg-secondary/50 p-1 ring-1 ring-border/50">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            const isHackathon = tab.id === "hackathon"
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-all sm:px-4 ${
                  isActive
                    ? isHackathon
                      ? "bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/20"
                      : "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
